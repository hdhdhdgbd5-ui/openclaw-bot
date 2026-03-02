# 🚀 CryptoTradeGenius

**Institutional-Grade AI-Powered Crypto Trading Bot**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Trade crypto automatically while you sleep. AI-powered risk management that never loses more than 2% per trade.**

---

## ✨ Features

### 🤖 AI Trading Engine
- **Machine Learning Ensemble**: Combines Random Forest and XGBoost models
- **Technical Analysis**: 20+ indicators (RSI, MACD, Bollinger Bands, ATR, etc.)
- **Real-time Predictions**: Analyzes market patterns and predicts price movements
- **Confidence Scoring**: Only trades when confidence exceeds threshold

### 🛡️ Risk Management (Institutional Grade)
- **Max 2% Risk Per Trade**: Never risk more than your set limit
- **Stop Loss & Take Profit**: Automatic position protection
- **Daily Loss Limits**: Circuit breakers to prevent major drawdowns
- **Position Sizing**: Kelly Criterion-inspired optimal sizing
- **Max Drawdown Protection**: Emergency stop at 20% drawdown

### 💼 Portfolio Management
- **Automatic Rebalancing**: Maintains target allocations
- **Multi-Asset Support**: Trade BTC, ETH, SOL, ADA, and more
- **Performance Tracking**: Real-time P&L and metrics

### 📊 Backtesting Engine
- **Historical Simulation**: Test strategies on past data
- **Performance Metrics**: Sharpe ratio, profit factor, win rate
- **Walk-forward Analysis**: Validate on out-of-sample data

### 📱 Telegram Notifications
- **Trade Alerts**: Instant notifications for all trades
- **Risk Alerts**: Critical events and circuit breakers
- **Daily Reports**: Performance summaries
- **Bot Commands**: Control your bot via Telegram

### 📝 Paper Trading
- **Risk-Free Testing**: Test strategies with virtual money
- **Real Market Data**: Trade on real prices, fake money
- **Strategy Validation**: Perfect your approach before going live

---

## 🏗️ Architecture

```
CryptoTradeGenius/
├── src/
│   ├── core/              # Trading engine & database
│   ├── exchanges/         # Exchange connectors (Binance, Coinbase)
│   ├── ai/               # ML prediction engine
│   ├── risk/             # Risk management system
│   ├── portfolio/        # Portfolio & rebalancing
│   ├── notifications/    # Telegram bot
│   ├── backtest/         # Backtesting framework
│   └── api/              # REST API & WebSocket
├── config/               # Configuration
├── data/                 # Database & storage
├── models/               # Trained ML models
└── logs/                 # Application logs
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/cryptotradegenius.git
cd cryptotradegenius
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Initialize Database

```bash
python main.py --init-db
```

### 4. Run in Paper Trading Mode

```bash
python main.py --paper
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRADING_MODE` | `paper` or `live` | `paper` |
| `MAX_RISK_PER_TRADE` | Max risk % per trade | `2.0` |
| `MAX_DAILY_LOSS` | Max daily loss % | `5.0` |
| `MAX_OPEN_POSITIONS` | Max concurrent trades | `10` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | - |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | - |
| `BINANCE_API_KEY` | Binance API key | - |
| `BINANCE_SECRET` | Binance secret | - |

---

## 💰 Monetization

### Performance Fee Model
- **20% of profits** - Industry standard
- High watermark - Only pay on new highs
- Monthly billing

### Subscription Model
- **Starter**: $199/month (5 trading pairs)
- **Pro**: $399/month (All pairs + advanced AI)
- **Enterprise**: $499/month (Custom strategies + dedicated support)

---

## 📡 API Documentation

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/engine/status` | GET | Trading engine status |
| `/engine/start` | POST | Start trading |
| `/engine/stop` | POST | Stop trading |
| `/portfolio/summary` | GET | Portfolio overview |
| `/trades` | GET | Trade history |
| `/risk/status` | GET | Risk metrics |
| `/signals` | GET | AI signals |

### WebSocket

Connect to `/ws` for real-time updates:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

---

## 🧪 Backtesting

```bash
# Run backtest via API
curl -X POST http://localhost:8000/backtest/run \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC/USDT", "ETH/USDT"],
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_balance": 10000
  }'
```

---

## 🚀 Deployment

### Render.com

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your fork
4. Add environment variables
5. Deploy!

The `render.yaml` blueprint is included for easy deployment.

### Railway

1. Install Railway CLI
2. Run `railway login`
3. Run `railway init`
4. Deploy with `railway up`

---

## 📱 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/status` | Bot status |
| `/portfolio` | Portfolio summary |
| `/trades` | Recent trades |
| `/pnl` | Profit/Loss |
| `/risk` | Risk status |
| `/stopbot` | Emergency stop |
| `/help` | Command list |

---

## 🛡️ Safety & Risk Disclaimer

⚠️ **IMPORTANT**: Crypto trading involves substantial risk of loss.

- Always start with **paper trading**
- Never risk more than you can afford to lose
- Past performance does not guarantee future results
- AI predictions are probabilistic, not guaranteed
- Use at your own risk

---

## 🔒 Security

- API keys stored securely (environment variables)
- Database encryption for sensitive data
- Rate limiting on API endpoints
- IP whitelisting support
- No private keys stored in code

---

## 📈 Performance Metrics

Track your bot's performance:

- **Win Rate**: % of profitable trades
- **Profit Factor**: Gross profit / Gross loss
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest peak-to-trough decline
- **Average Trade**: Mean profit per trade

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- [CCXT](https://github.com/ccxt/ccxt) - Exchange connectivity
- [TA-Lib](https://ta-lib.org/) - Technical analysis
- [scikit-learn](https://scikit-learn.org/) - Machine learning
- [FastAPI](https://fastapi.tiangolo.com/) - API framework

---

## 📞 Support

- 📧 Email: support@cryptotradegenius.com
- 💬 Telegram: @CryptoTradeGeniusSupport
- 🐛 Issues: GitHub Issues

---

**Made with 💙 by CryptoTradeGenius Team**

*Trade smart. Trade safe. Trade with AI.*
