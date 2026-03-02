#!/usr/bin/env node
/**
 * DIVINE ALGORITHM - The God-Mode Trading AI
 * Arbitrage Monitor - Node.js version
 */

const https = require('https');

// Configuration
const CHECK_INTERVAL = 30000; // 30 seconds
const MIN_ARBITRAGE_PERCENT = 0.5;

// Major crypto pairs
const PAIRS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT"
];

// CoinGecko IDs for reference prices
const COINGECKO_IDS = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "BNBUSDT": "binancecoin",
    "SOLUSDT": "solana",
    "XRPUSDT": "ripple",
    "ADAUSDT": "cardano",
    "DOGEUSDT": "dogecoin",
    "AVAXUSDT": "avalanche-2",
    "DOTUSDT": "polkadot",
    "MATICUSDT": "matic-network"
};

function fetchBinance(symbol) {
    return new Promise((resolve, reject) => {
        const url = `https://api.binance.com/api/v3/ticker/price?symbol=${symbol}`;
        https.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    resolve(parseFloat(json.price));
                } catch (e) {
                    resolve(null);
                }
            });
        }).on('error', () => resolve(null));
    });
}

function fetchCoinGecko(coinId) {
    return new Promise((resolve, reject) => {
        const url = `https://api.coingecko.com/api/v3/simple/price?ids=${coinId}&vs_currencies=usd`;
        https.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    resolve(json[coinId]?.usd || null);
                } catch (e) {
                    resolve(null);
                }
            });
        }).on('error', () => resolve(null));
    });
}

async function checkArbitrage(symbol) {
    const opportunities = [];
    
    // Get prices from exchanges
    const prices = {};
    
    // Binance
    const binancePrice = await fetchBinance(symbol);
    if (binancePrice) prices['Binance'] = binancePrice;
    
    // CoinGecko as reference
    const cgId = COINGECKO_IDS[symbol];
    if (cgId) {
        const cgPrice = await fetchCoinGecko(cgId);
        if (cgPrice) prices['CoinGecko'] = cgPrice;
    }
    
    if (Object.keys(prices).length < 2) return [];
    
    // Find price differences
    const priceValues = Object.values(prices);
    const minPrice = Math.min(...priceValues);
    const maxPrice = Math.max(...priceValues);
    
    const diffPercent = ((maxPrice - minPrice) / minPrice) * 100;
    
    if (diffPercent >= MIN_ARBITRAGE_PERCENT) {
        const minExchange = Object.keys(prices).find(k => prices[k] === minPrice);
        const maxExchange = Object.keys(prices).find(k => prices[k] === maxPrice);
        
        opportunities.push({
            symbol,
            buy_exchange: minExchange,
            sell_exchange: maxExchange,
            buy_price: minPrice,
            sell_price: maxPrice,
            profit_percent: diffPercent.toFixed(2),
            timestamp: new Date().toISOString()
        });
    }
    
    return opportunities;
}

async function scanAll() {
    console.log('\n' + '='.repeat(60));
    console.log('DIVINE ALGORITHM - Arbitrage Scanner');
    console.log('Time:', new Date().toISOString());
    console.log('='.repeat(60));
    
    let allOps = [];
    
    for (const pair of PAIRS) {
        const ops = await checkArbitrage(pair);
        if (ops.length > 0) {
            allOps = allOps.concat(ops);
            for (const op of ops) {
                console.log(`🚨 ARBITRAGE: ${op.symbol}`);
                console.log(`   Buy at ${op.buy_exchange}: $${op.buy_price.toLocaleString()}`);
                console.log(`   Sell at ${op.sell_exchange}: $${op.sell_price.toLocaleString()}`);
                console.log(`   Profit: ${op.profit_percent}%`);
            }
        } else {
            console.log(`✅ ${pair}: No arbitrage`);
        }
    }
    
    return allOps;
}

async function main() {
    console.log('🚀 DIVINE ALGORITHM started!');
    console.log(`Monitoring ${PAIRS.length} pairs every ${CHECK_INTERVAL/1000}s`);
    console.log(`Minimum arbitrage threshold: ${MIN_ARBITRAGE_PERCENT}%`);
    
    // Initial scan
    await scanAll();
    
    // Continuous monitoring
    setInterval(async () => {
        await scanAll();
    }, CHECK_INTERVAL);
}

main();
