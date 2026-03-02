# ⛓️ Solidity - Smart Contract Programming

**Build DeFi protocols, NFTs, and decentralized applications**

## What You Can Build

| Application | Description | Income Potential |
|-------------|-------------|------------------|
| **DeFi Protocols** | AMMs, lending platforms, stablecoins | $10K-100K/project |
| **NFT Marketplaces** | Digital art, gaming assets | $5K-50K/project |
| **Smart Contract Audits** | Security reviews | $5K-50K/audit |
| **Token Launches** | ERC-20, ERC-721 tokens | $2K-20K/project |
| **DAOs** | Governance systems | $10K-100K/project |

---

## 📚 Learning Path

### Week 1: Basics
1. Data types (uint, address, bytes32, bool)
2. Functions (public, private, view, pure)
3. Storage vs Memory
4. Events and Logging

### Week 2: Intermediate
1. Inheritance and Interfaces
2.Modifiers
3. Libraries
4. Gas optimization

### Week 3: Advanced
1. Proxy patterns
2. Upgradeable contracts
3. Diamond standard
4. Formal verification with Certora

### Week 4: Expert
1. Flash loans
2. Cross-chain bridges
3. MEV strategies
4. Smart contract audits

---

## 💻 Your First Smart Contract

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title SimpleStorage - A basic storage contract
/// @notice Demonstrates fundamental Solidity concepts
contract SimpleStorage {
    // State variable - stored on blockchain
    uint256 private storedValue;
    
    // Event for tracking changes
    event ValueStored(uint256 newValue, address setter);
    
    // Custom error
    error ValueTooHigh(uint256 value, uint256 max);
    
    /// @notice Store a value
    /// @param _value The value to store
    function setValue(uint256 _value) external {
        if (_value > 1000) {
            revert ValueTooHigh({value: _value, max: 1000});
        }
        storedValue = _value;
        emit ValueStored(_value, msg.sender);
    }
    
    /// @notice Retrieve the stored value
    /// @return The stored value
    function getValue() external view returns (uint256) {
        return storedValue;
    }
}
```

---

## 🔥 DeFi Token Contract (ERC-20)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title EmpireToken - A deflationary token with auto-staking
/// @notice Demonstrates advanced ERC-20 patterns
contract EmpireToken is ERC20, Ownable {
    
    // Tax configuration
    uint256 public buyTaxPercent = 2;
    uint256 public sellTaxPercent = 5;
    
    // Auto-staking mechanism
    mapping(address => uint256) public stakedAmounts;
    uint256 public totalStaked;
    
    // Excluded from tax
    mapping(address => bool) public isExcludedFromTax;
    
    // Events
    event Staked(address user, uint256 amount);
    event Unstaked(address user, uint256 amount);
    event TaxCollected(uint256 amount);
    
    constructor() ERC20("Empire Token", "EMP") Ownable(msg.sender) {
        // Mint total supply to deployer
        _mint(msg.sender, 1_000_000_000 * 10**decimals());
        
        // Exclude contract from tax
        isExcludedFromTax[address(this)] = true;
        isExcludedFromTax[msg.sender] = true;
    }
    
    /// @notice Transfer with automatic tax
    function _transfer(
        address from,
        address to,
        uint256 amount
    ) internal virtual override {
        // Calculate tax on sells
        uint256 tax = 0;
        if (!isExcludedFromTax[from] && !isExcludedFromTax[to]) {
            if (sellTaxPercent > 0) {
                tax = (amount * sellTaxPercent) / 100;
                super._transfer(from, address(this), tax);
                emit TaxCollected(tax);
            }
        }
        
        uint256 transferAmount = amount - tax;
        super._transfer(from, to, transferAmount);
    }
    
    /// @notice Stake tokens for rewards
    function stake(uint256 amount) external {
        require(amount > 0, "Cannot stake 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        
        _transfer(msg.sender, address(this), amount);
        stakedAmounts[msg.sender] += amount;
        totalStaked += amount;
        
        emit Staked(msg.sender, amount);
    }
    
    /// @notice Unstake tokens
    function unstake(uint256 amount) external {
        require(amount > 0, "Cannot unstake 0");
        require(stakedAmounts[msg.sender] >= amount, "Insufficient staked");
        
        stakedAmounts[msg.sender] -= amount;
        totalStaked -= amount;
        _transfer(address(this), msg.sender, amount);
        
        emit Unstaked(msg.sender, amount);
    }
}
```

---

## 🎮 NFT Collection (ERC-721)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title EmpireNFT - NFT collection with royalty support
contract EmpireNFT is ERC721, ERC721URIStorage, Ownable {
    
    uint256 public nextTokenId;
    uint256 public royaltyPercent = 10; // 10% royalty
    
    // Mapping from token ID to creator
    mapping(uint256 => address) public tokenCreators;
    
    // Event for minting
    event Minted(address indexed to, uint256 tokenId, string uri);
    
    constructor() ERC721("Empire NFT", "EMPNFT") Ownable(msg.sender) {}
    
    /// @notice Mint a new NFT
    function mint(string memory uri) external returns (uint256) {
        uint256 tokenId = nextTokenId;
        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, uri);
        tokenCreators[tokenId] = msg.sender;
        nextTokenId++;
        
        emit Minted(msg.sender, tokenId, uri);
        return tokenId;
    }
    
    /// @notice Get royalty info for a sale
    function royaltyInfo(
        uint256 tokenId,
        uint256 salePrice
    ) external view returns (address receiver, uint256 royaltyAmount) {
        receiver = tokenCreators[tokenId];
        royaltyAmount = (salePrice * royaltyPercent) / 100;
    }
    
    // Required overrides
    function tokenURI(uint256 tokenId)
        public view override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId)
        public view override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
```

---

## 🔐 Security Best Practices

### 1. Reentrancy Guard
```solidity
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract SecureVault is ReentrancyGuard {
    mapping(address => uint256) public balances;
    
    function withdraw() external nonReentrant {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "No balance");
        
        balances[msg.sender] = 0;
        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");
    }
}
```

### 2. Access Control
```solidity
import "@openzeppelin/contracts/access/AccessControl.sol";

contract AdminContract is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    
    constructor() {
        _grantRole(ADMIN_ROLE, msg.sender);
    }
    
    function restrictedFunction() external onlyRole(ADMIN_ROLE) {
        // Only admins can call
    }
}
```

---

## 🛠️ Development Tools

| Tool | Purpose |
|------|---------|
| **Remix IDE** | Browser-based IDE |
| **Hardhat** | Local development network |
| **Foundry** | Fast testing & deployment |
| **OpenZeppelin** | Secure contract library |
| **Ethers.js** | JavaScript interaction |
| **Waffle** | Smart contract testing |

---

## 📖 Exercises

### Exercise 1: Token Faucet
Build a contract that:
- Allows anyone to claim free tokens (once)
- Tracks claimed addresses
- Has an owner who can refill

### Exercise 2: Simple Lottery
Build a lottery that:
- Collects ETH during a period
- Randomly selects winner
- Sends prize to winner

### Exercise 3: Token Swap
Build a basic AMM that:
- Has two token pools
- Prices based on constant product
- Allows swapping

---

## 🎯 Next Steps

1. ✅ Complete exercises above
2. 📚 Study OpenZeppelin contracts
3. 🔍 Read smart contract hacks (Ethernaut)
4. 🛡️ Learn security patterns
5. 🎓 Get certified (CertiK, Trail of Bits)

**Happy Building! 🚀**
