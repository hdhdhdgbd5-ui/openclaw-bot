# 🦀 Rust for Blockchain & Crypto

**Build high-performance crypto protocols, bridges, and DeFi**

## What You Can Build

| Application | Description | Income Potential |
|-------------|-------------|------------------|
| **Solana Programs** | High-speed dApps | $15K-100K/project |
| **Aptos Move Modules** | Modern L2 contracts | $10K-80K/project |
| **Cross-chain Bridges** | Asset transfers | $20K-150K/project |
| **MEV Bots** | Maximal extractable value | $50K-500K/year |
| **Trading Engines** | High-frequency trading | $100K-500K/year |
| **Crypto Wallets** | Secure multi-sig | $10K-50K/project |

---

## 📚 Learning Path

### Week 1: Rust Fundamentals
1. Ownership & Borrowing
2. Data types & Control flow
3. Structs, Enums, Pattern matching
4. Error handling (Result, Option)

### Week 2: Advanced Rust
1. Lifetimes
2. Traits & Generics
3. Concurrency (async/await, tokio)
4. Unsafe Rust

### Week 3: Crypto-Specific
1. Cryptographic libraries (ring, libsodium)
2. Serialization (borsh, serde)
3. Merkle trees & Hashing
4. Elliptic curves (k256, ed25519)

### Week 4: Blockchain Development
1. Solana/Anchor framework
2. Move language (Aptos)
3. Substrate (Polkadot)
4. Build a DEX

---

## 💻 Core Rust Examples

### Ownership & Borrowing
```rust
// The key to Rust's memory safety - ownership rules:
// 1. Each value has one owner
// 2. When owner goes out of scope, value is dropped
// 3. Only one mutable reference OR multiple immutable references

fn main() {
    // Ownership transfer
    let s1 = String::from("hello");
    let s2 = s1; // s1 is "moved" to s2
    // println!("{}", s1); // ERROR: s1 no longer valid
    
    // Borrowing - reference without ownership
    let s3 = String::from("world");
    let len = calculate_length(&s3); // borrow s3
    println!("Length of '{}' is {}", s3, len); // s3 still valid
    
    // Mutable reference
    let mut s4 = String::from("hello");
    modify_string(&mut s4);
    println!("{}", s4); // "hello, world"
}

fn calculate_length(s: &String) -> usize {
    s.len()
}

fn modify_string(s: &mut String) {
    s.push_str(", world");
}
```

### Error Handling
```rust
use std::fs::File;
use std::io::Read;

// Propagate errors with ?
fn read_config() -> Result<String, std::io::Error> {
    let mut file = File::open("config.json")?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}

// Custom error types
#[derive(Debug)]
enum CryptoError {
    InvalidSignature,
    InsufficientFunds,
    Overflow,
    InvalidAddress,
}

impl std::fmt::Display for CryptoError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            CryptoError::InvalidSignature => write!(f, "Invalid signature"),
            CryptoError::InsufficientFunds => write!(f, "Insufficient funds"),
            CryptoError::Overflow => write!(f, "Integer overflow"),
            CryptoError::InvalidAddress => write!(f, "Invalid address"),
        }
    }
}

impl std::error::Error for CryptoError {}
```

---

## 🔐 Cryptographic Operations

### Hashing & Merkle Trees
```rust
use sha2::{Sha256, Digest};
use std::collections::HashMap;

/// Simple Merkle Tree implementation
pub struct MerkleTree {
    leaves: Vec<Vec<u8>>,
    nodes: HashMap<u32, Vec<Vec<u8>>>,
}

impl MerkleTree {
    /// Create new Merkle tree from leaves
    pub fn new(leaves: Vec<Vec<u8>>) -> Self {
        let mut tree = MerkleTree {
            leaves: leaves.clone(),
            nodes: HashMap::new(),
        };
        tree.build();
        tree
    }
    
    fn hash_pair(left: &[u8], right: &[u8]) -> Vec<u8> {
        let mut hasher = Sha256::new();
        hasher.update(left);
        hasher.update(right);
        hasher.finalize().to_vec()
    }
    
    fn build(&mut self) {
        let mut current_level = self.leaves.clone();
        let mut level = 0;
        
        while current_level.len() > 1 {
            let mut next_level = Vec::new();
            
            for chunk in current_level.chunks(2) {
                if chunk.len() == 2 {
                    let hash = Self::hash_pair(&chunk[0], &chunk[1]);
                    next_level.push(hash);
                } else {
                    // Duplicate odd node
                    let hash = Self::hash_pair(&chunk[0], &chunk[0]);
                    next_level.push(hash);
                }
            }
            
            self.nodes.insert(level, current_level);
            current_level = next_level;
            level += 1;
        }
        
        self.nodes.insert(level, current_level);
    }
    
    /// Get merkle root
    pub fn root(&self) -> Option<&Vec<u8>> {
        self.nodes.get(&0).and_then(|v| v.first())
    }
    
    /// Generate proof for leaf at index
    pub fn proof(&self, index: usize) -> Vec<(Vec<u8>, bool)> {
        let mut proof = Vec::new();
        let mut current_index = index;
        
        for level in 0..self.nodes.len() {
            if let Some(nodes) = self.nodes.get(&level) {
                if current_index >= nodes.len() {
                    break;
                }
                
                let sibling_index = if current_index % 2 == 0 {
                    current_index + 1
                } else {
                    current_index - 1
                };
                
                if sibling_index < nodes.len() {
                    let is_left = current_index % 2 != 0;
                    proof.push((nodes[sibling_index].clone(), is_left));
                }
                
                current_index /= 2;
            }
        }
        
        proof
    }
}
```

### ECDSA Signature Verification
```rust
use k256::ecdsa::{SigningKey, VerifyingKey, Signature, signature::Signer};
use k256::elliptic_curve::rand_core::OsRng;

/// Generate keypair
fn generate_keypair() -> (SigningKey, VerifyingKey) {
    let signing_key = SigningKey::random(&mut OsRng);
    let verifying_key = VerifyingKey::from(&signing_key);
    (signing_key, verifying_key)
}

/// Sign a message
fn sign_message(signing_key: &SigningKey, message: &[u8]) -> Signature {
    let signature: Signature = signing_key.sign(message);
    signature
}

/// Verify a signature
fn verify_signature(verifying_key: &VerifyingKey, message: &[u8], signature: &Signature) -> bool {
    verifying_key.verify(message, signature).is_ok()
}

/// Crypto wallet address derivation
fn derive_address(verifying_key: &VerifyingKey) -> String {
    // Keccak256 hash of compressed public key, take last 20 bytes
    use sha3::{Keccak256, Digest};
    
    let mut hasher = Keccak256::new();
    hasher.update(verifying_key.to_encoded_point(false).as_bytes());
    let result = hasher.finalize();
    
    // Take last 20 bytes, add 0x prefix
    format!("0x{}", hex::encode(&result[12..32]))
}
```

---

## ⛓️ Solana Program Example

```rust
use anchor_lang::prelude::*;
use anchor_lang::solana_program::{program::invoke, system_instruction};

declare_id!("EMP111111111111111111111111111111111111");

#[program]
pub mod empire_token {
    use super::*;
    
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        ctx.accounts.authority = ctx.accounts.user.key();
        ctx.accounts.supply = 1_000_000_000;
        ctx.accounts.decimals = 9;
        Ok(())
    }
    
    pub fn transfer(ctx: Context<Transfer>, amount: u64) -> Result<()> {
        require!(amount > 0, ErrorCode::InvalidAmount);
        require!(
            ctx.accounts.from.amount >= amount,
            ErrorCode::InsufficientFunds
        );
        
        ctx.accounts.from.amount -= amount;
        ctx.accounts.to.amount += amount;
        
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = user,
        space = 8 + TokenAccount::INIT_SPACE,
        seeds = [b"token"],
        bump
    )]
    pub token: Account<'info, TokenAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Transfer<'info> {
    #[account(mut)]
    pub from: Account<'info, TokenAccount>,
    #[account(mut)]
    pub to: Account<'info, TokenAccount>,
    pub authority: Signer<'info>,
}

#[account]
#[derive(InitSpace)]
pub struct TokenAccount {
    pub authority: Pubkey,
    pub supply: u64,
    pub decimals: u8,
    pub amount: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Invalid amount")]
    InvalidAmount,
    #[msg("Insufficient funds")]
    InsufficientFunds,
}
```

---

## 🚀 High-Performance Trading Bot

```rust
use tokio::sync::mpsc;
use std::sync::Arc;

/// Order types
#[derive(Debug, Clone)]
pub enum OrderType {
    Market,
    Limit { price: f64 },
}

#[derive(Debug, Clone)]
pub enum Side {
    Buy,
    Sell,
}

#[derive(Debug, Clone)]
pub struct Order {
    pub id: u64,
    pub side: Side,
    pub amount: f64,
    pub order_type: OrderType,
    pub symbol: String,
}

/// Order book for a trading pair
pub struct OrderBook {
    bids: Vec<(f64, f64)>, // (price, amount)
    asks: Vec<(f64, f64)>,
}

impl OrderBook {
    pub fn new() -> Self {
        OrderBook {
            bids: Vec::new(),
            asks: Vec::new(),
        }
    }
    
    /// Add order to book
    pub fn add_order(&mut self, side: Side, price: f64, amount: f64) {
        match side {
            Side::Buy => self.bids.push((price, amount)),
            Side::Sell => self.asks.push((price, amount)),
        }
    }
    
    /// Get best bid/ask
    pub fn spread(&self) -> Option<(f64, f64)> {
        let best_bid = self.bids.iter().max_by_key(|(p, _)| p)?;
        let best_ask = self.bids.iter().min_by_key(|(p, _)| p)?;
        Some((*best_bid.0, *best_ask.0))
    }
    
    /// Match orders (simple FIFO)
    pub fn match_orders(&mut self) -> Vec<(f64, f64)> {
        let mut trades = Vec::new();
        
        // Sort by price
        self.bids.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
        self.asks.sort();
        
        while let (Some(bid), Some(ask)) = (self.bids.last(), self.asks.last()) {
            if bid.0 >= ask.0 {
                let trade_price = ask.0;
                let trade_amount = bid.1.min(ask.1);
                trades.push((trade_price, trade_amount));
                
                // Update quantities
                let (new_bid, new_ask) = (
                    (bid.0, bid.1 - trade_amount),
                    (ask.0, ask.1 - trade_amount)
                );
                
                if new_bid.1 <= 0 {
                    self.bids.pop();
                } else {
                    self.bids.last_mut().unwrap().1 = new_bid.1;
                }
                
                if new_ask.1 <= 0 {
                    self.asks.pop();
                } else {
                    self.asks.last_mut().unwrap().1 = new_ask.1;
                }
            } else {
                break;
            }
        }
        
        trades
    }
}

/// Trading engine running async
pub async fn trading_engine(
    mut order_rx: mpsc::Receiver<Order>,
    book: Arc<tokio::sync::Mutex<OrderBook>>,
) {
    while let Some(order) = order_rx.recv().await {
        let mut book = book.lock().await;
        
        match order.side {
            Side::Buy => book.add_order(Side::Buy, match order.order_type {
                OrderType::Market => f64::MAX,
                OrderType::Limit { price } => price,
            }, order.amount),
            Side::Sell => book.add_order(Side::Sell, match order.order_type {
                OrderType::Market => 0.0,
                OrderType::Limit { price } => price,
            }, order.amount),
        }
        
        // Try to match orders
        let trades = book.match_orders();
        for (price, amount) in trades {
            println!("TRADE: {} @ {}", amount, price);
        }
    }
}
```

---

## 🛠️ Development Tools

| Tool | Purpose |
|------|---------|
| **Cargo** | Package manager & build tool |
| **Rustup** | Rust toolchain manager |
| **Anchor** | Solana framework |
| **Substrate** | Polkadot SDK |
| **Tokio** | Async runtime |
| **Clippy** | Linter |
| **Miri** | Undefined behavior checker |

---

## 📖 Exercises

### Exercise 1: CLI Wallet
Build a CLI that:
- Generates keypairs
- Signs/verifies messages
- Derives addresses

### Exercise 2: Token Swap
Build a constant-product AMM:
- Two-token pool
- Swap function with price calculation
- Add/remove liquidity

### Exercise 3: MEV Bot
Build a sandwich bot that:
- Monitors mempool
- Front-runs large trades
- Back-runs to capture spread

---

## 🎯 Next Steps

1. ✅ Complete Rustlings exercises
2. 📚 Build on Solana with Anchor
3. 🔒 Study crypto vulnerabilities
4. 📖 Read "Programming Bitcoin"
5. 🏆 Participate in hackathons

**Start building! 🚀**
