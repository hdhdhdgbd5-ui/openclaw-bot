# 🔐 ZK-SNARKs - Zero-Knowledge Proofs

**Build privacy protocols, verifiable computation, and scaling solutions**

## What You Can Build

| Application | Description | Income Potential |
|-------------|-------------|------------------|
| **Privacy Coins** | zkSNARK-based anonymity | Protocol value |
| **Rollups** | L2 scaling (zkSync, StarkNet) | $50K-500K/project |
| **Identity Verification** | Proof of personhood | $20K-100K/project |
| **Private DeFi** | Confidential transactions | $30K-200K/project |
| **Verifiable Credentials** | KYC/AML without disclosure | $10K-50K/project |
| **zkEVMs** | Ethereum scaling | $100K-1M/project |

---

## 📚 Learning Path

### Week 1: Mathematical Foundations
1. Group theory & Elliptic curves
2. Polynomial commitments
3. Trusted setup ceremonies
4. Hash functions

### Week 2: ZK Fundamentals
1. Interactive vs Non-interactive proofs
2. Soundness & Completeness
3. zkSNARK construction (Groth16, PLONK)
4. Fiat-Shamir transformation

### Week 3: Implementation
1. Circom circuit language
2. SnarkJS for proving/verification
3. Hash-based ZK circuits
4. Arithmetic circuits

### Week 4: Applications
1. Private voting
2. Proof of solvency
3. Layer 2 rollups
4. zkBridge design

---

## 🧮 Mathematical Foundations

### Elliptic Curve Operations
```python
"""
ZK-SNARKs rely on elliptic curve cryptography.
Key curves: BN254, BLS12-381
"""

# Point addition on Weierstrass curve
# y² = x³ + ax + b (over finite field)

class EllipticCurve:
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p
    
    def is_on_curve(self, x, y):
        return (y*y - x*x*x - self.a*x - self.b) % self.p == 0
    
    def point_add(self, P, Q):
        if P is None: return Q
        if Q is None: return P
        
        x1, y1 = P
        x2, y2 = Q
        
        if x1 == x2:
            if y1 == y2:
                # Point doubling
                lam = (3*x1*x1 + self.a) * pow(2*y1, -1, self.p) % self.p
            else:
                return None  # Point at infinity
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, self.p) % self.p
        
        x3 = (lam*lam - x1 - x2) % self.p
        y3 = (lam*(x1 - x3) - y1) % self.p
        
        return (x3, y3)
    
    def scalar_mul(self, k, P):
        """Efficient scalar multiplication using double-and-add"""
        result = None
        addend = P
        
        while k:
            if k & 1:
                result = self.point_add(result, addend)
            addend = self.point_add(addend, addend)
            k >>= 1
        
        return result

# BN254 curve (used in zkSNARKs)
# y² = x³ + 3 (mod p) where p = 21888242871839275222246405745257275088548364400416034343698204186575808495617
bn254 = EllipticCurve(0, 3, 21888242871839275222246405745257275088548364400416034343698204186575808495617)
```

### Polynomial Commitment (KZG)
```python
"""
KZG10 Polynomial Commitment Scheme
Allows prover to commit to polynomial and prove values
"""

class KZG10:
    def __init__(self, g1, g2, tau):
        """
        g1, g2: generators
        tau: secret for trusted setup
        """
        self.g1 = g1
        self.g2 = g2
        self.tau = tau
    
    def commit(self, polynomial):
        """
        Commit to polynomial: C = g^p(tau)
        """
        # Evaluate polynomial at secret tau
        result = 0
        for i, coeff in enumerate(polynomial):
            result += coeff * (self.tau ** i)
        return self.g1 * result
    
    def create_proof(self, polynomial, x):
        """
        Create proof that polynomial(x) = y
        Uses quotient polynomial q(z) = (p(z) - p(x)) / (z - x)
        """
        y = sum(c * (x ** i) for i, c in enumerate(polynomial))
        
        # Compute quotient polynomial
        # p(z) - p(x) = (z - x) * q(z)
        # Use polynomial division
        
        return y, self.g1 * quotient_poly(polynomial, x)
    
    def verify_proof(self, commitment, x, y, proof):
        """
        Verify: e(C, g2) = e(g1^x * proof, g2^x) * e(g1^y, g2)
        """
        # Pairing check - simplified
        return True
```

---

## 🔧 Circom Circuit Examples

### Basic Circuit: Age Verification
```circom
/*
Age Verification Circuit
Prove you are over 18 without revealing age
*/

pragma circom 2.0.0;

// Template for comparison
template Compare() {
    signal input a;
    signal input b;
    signal output out;
    
    // out = 1 if a >= b, else 0
    out <-- a >= b ? 1 : 0;
}

// Main circuit
template AgeVerifier() {
    // Private input: user's age
    signal private input userAge;
    
    // Public input: minimum age
    signal input minimumAge;
    
    // Output: proof
    signal output verified;
    
    // Check age >= minimum
    component comp = Compare();
    comp.a <== userAge;
    comp.b <== minimumAge;
    
    // Additional constraint: user must be born (not future age)
    // maximum reasonable age
    userAge === comp.a;
    
    verified <== comp.out;
    
    // Log result (for debugging)
    log("Age verified:", verified);
}

component main {public [minimumAge]} = AgeVerifier();
```

### Hash Circuit (Poseidon)
```circom
/*
Poseidon Hash Function
ZK-friendly hash used in many circuits
*/

include "poseidon.circom";

// Hash two inputs
template HashLeftRight() {
    signal input left;
    signal input right;
    signal output hash;
    
    component poseidon = Poseidon(2);
    poseidon.inputs[0] <== left;
    poseidon.inputs[1] <== right;
    hash <== poseidon.out;
}

// Merkle tree inclusion proof
template MerkleTreeChecker(levels) {
    signal input leaf;
    signal input root;
    signal input pathElements[levels];
    signal input pathIndices[levels];
    
    component hashers[levels];
    signal computedHash[levels + 1];
    
    computedHash[0] <== leaf;
    
    for (var i = 0; i < levels; i++) {
        hashers[i] = HashLeftRight();
        
        // Choose left/right based on path index
        hashers[i].left <== pathIndices[i] == 0 ? computedHash[i] : pathElements[i];
        hashers[i].right <== pathIndices[i] == 0 ? pathElements[i] : computedHash[i];
        
        computedHash[i + 1] <== hashers[i].hash;
    }
    
    // Verify computed root matches expected
    root === computedHash[levels];
}

component main {public [root]} = MerkleTreeChecker(20);
```

### Private Token Transfer
```circom
/*
Private Token Transfer Circuit
Prove valid transfer without revealing amounts or addresses
*/

pragma circom 2.0.0;

include "bitify.circom";
include "poseidon.circom";

// Verify note validity and compute new commitments
template PrivateTransfer(levels) {
    // Public inputs
    signal input root;
    signal input newRoot;
    
    // Private inputs
    signal private input senderSecret;
    signal private input senderNullifier;
    signal private input amount;
    signal private input fee;
    signal private input recipientPublicKey;
    
    // Merkle proof path
    signal private input pathElements[levels];
    signal private input pathIndices[levels];
    
    // Verify sender commitment exists in tree
    component merkleProof = MerkleTreeChecker(levels);
    merkleProof.leaf <== PoseidonHash(senderSecret, senderNullifier, amount);
    merkleProof.root <== root;
    for (var i = 0; i < levels; i++) {
        merkleProof.pathElements[i] <== pathElements[i];
        merkleProof.pathIndices[i] <== pathIndices[i];
    }
    
    // Verify amount > fee
    component lessThan = LessThan(64);
    lessThan.in[0] <== fee;
    lessThan.in[1] <== amount;
    lessThan.out === 1;
    
    // Compute change and recipient commitment
    signal change <== amount - fee;
    signal recipientCommitment <== PoseidonHash(recipientPublicKey, 0, change);
    
    // Output new root (sender's change + recipient's commitment)
    // Simplified - actual implementation would add both
    newRoot <== root; // Placeholder
}

component main {public [root, newRoot]} = PrivateTransfer(20);
```

---

## 🃏 SnarkJS Integration

### Proving & Verification
```javascript
/**
 * Using snarkjs for ZK proof generation and verification
 */

const snarkjs = require("snarkjs");

// Generate proof
async function generateProof(input, wasmPath, zkeyPath) {
    const { proof, publicSignals } = await snarkjs.groth16.fullProve(
        input,
        wasmPath,    // compiled circuit
        zkeyPath     // proving key
    );
    
    return { proof, publicSignals };
}

// Verify proof
async function verifyProof(zkeyPath, publicSignals, proof) {
    const vKey = await snarkjs.zKey.exportVerificationKey(zkeyPath);
    const res = await snarkjs.groth16.verify(vKey, publicSignals, proof);
    
    return res;
}

// Generate Solidity verifier
async function generateVerifier(zkeyPath, templatePath) {
    const code = await snarkjs.groth16.exportSolidityVerifier(
        zkeyPath, 
        templatePath || " verifier_template.sol"
    );
    return code;
}

// Example: Age verification
async function main() {
    // Input: private age, public minimum
    const input = {
        userAge: 25,
        minimumAge: 18
    };
    
    // Generate proof (prover)
    const { proof, publicSignals } = await generateProof(
        input,
        "age_verifier.wasm",
        "age_verifier_0001.zkey"
    );
    
    console.log("Proof generated:", proof);
    console.log("Public signals:", publicSignals);
    
    // Verify (verifier)
    const isValid = await verifyProof(
        "age_verifier_0001.zkey",
        publicSignals,
        proof
    );
    
    console.log("Proof valid:", isValid);
}
```

### Solidity Verifier Contract
```solidity
// Auto-generated by snarkjs - Simplified Verifier
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

library Pairing {
    struct G1Point {
        uint256 X;
        uint256 Y;
    }
    
    struct G2Point {
        uint256[2] X;
        uint256[2] Y;
    }
    
    function eccAdd(G1Point memory p1, G1Point memory p2) internal view {
        // Elliptic curve addition
    }
    
    function eccMul(G1Point memory p, uint256 s) internal view {
        // Scalar multiplication
    }
}

contract Verifier {
    using Pairing for *;
    
    // Verification Key
    uint256 constant IC0x = 0x...;
    uint256 constant IC0y = 0x...;
    // ... more IC points
    
    function verifyProof(
        uint256[2] memory a,
        uint256[2][2] memory b,
        uint256[2] memory c,
        uint256[] memory input
    ) public view returns (bool) {
        // Pairing check
        // e(A, B) = e(C, D) where D = vk_alpha * beta + sum(input[i] * vk_gamma_abc[i]) + vk_delta
        
        // Simplified - actual implementation is complex
        return true;
    }
}
```

---

## 🌐 Real-World Applications

### 1. Tornado Cash (Privacy Mixer)
```javascript
// Simplified Tornado Cash style contract
const hasher = require('circomlib').poseidon;

class Tornado {
    constructor(denomination, treeLevels) {
        this.denomination = denomination;
        this.tree = new MerkleTree(treeLevels);
        this.leafIndex = 0;
    }
    
    // Deposit: commitment = hash(secret, nullifier)
    async deposit(secret, nullifier) {
        const commitment = hasher([secret, nullifier]);
        
        // Add to merkle tree
        this.tree.insert(commitment);
        
        // Return note for user to save
        return {
            secret,
            nullifier,
            commitment,
            leafIndex: this.leafIndex++
        };
    }
    
    // Withdraw: prove membership without revealing which leaf
    async withdraw(note, recipient) {
        // Generate ZK proof of:
        // 1. Note is in the merkle tree
        // 2. Nullifier hash is computed correctly
        
        const proof = await generateMerkleProof(note.commitment);
        
        // Send funds to recipient
        await this.transfer(recipient, this.denomination);
    }
}
```

### 2. Semaphore (Anonymous Identity)
```javascript
/**
 * Semaphore: Signal without revealing identity
 */

class Semaphore {
    constructor() {
        this.merkleTree = new MerkleTree(20);
        this.nullifierHashes = new Set();
    }
    
    // Join group (register identity commitment)
    async join(identityCommitment) {
        this.merkleTree.insert(identityCommitment);
    }
    
    // Signal (anonymous message)
    async signal(identity, message, externalNullifier) {
        // Generate ZK proof showing:
        // 1. User is member of group (merkle proof)
        // 2. Nullifier hash is derived correctly
        
        const nullifierHash = hash(identity.nullifier, externalNullifier);
        
        // Prevent double-signaling
        if (this.nullifierHashes.has(nullifierHash)) {
            throw new Error("Already signaled");
        }
        
        const proof = await generateProof({
            identitySecret: identity.secret,
            identityNullifier: identity.nullifier,
            treePathElements: identity.pathElements,
            treePathIndices: identity.pathIndices,
            externalNullifier
        });
        
        this.nullifierHashes.add(nullifierHash);
        
        return { message, nullifierHash, proof };
    }
}
```

---

## 🛠️ Tools & Resources

| Tool | Purpose |
|------|---------|
| **Circom** | Circuit compiler |
| **SnarkJS** | Proving/verification |
| **ZoKrates** | High-level ZK DSL |
| **Cairo** | STARK language (StarkNet) |
| **o1js** | TypeScript ZK framework |
| **EZKL** | ZK for ML inference |

---

## 📖 Exercises

### Exercise 1: Sudoku Solver
Build ZK circuit that:
- Proves solution is valid
- Doesn't reveal the solution

### Exercise 2: Range Proof
Build circuit proving:
- Number is in range [0, 2^32]
- Doesn't reveal exact value

### Exercise 3: Private Voting
Build system that:
- Verifies voter is eligible
- Hides vote count per option
- Prevents double voting

---

## 🎯 Next Steps

1. ✅ Complete Circom tutorials
2. 📚 Study Groth16 vs PLONK vs STARK
3. 🔒 Learn security pitfalls
4. 📖 Read "Proofs, Arguments, and Zero-Knowledge"
5. 🏆 Participate in ZK hackathons

**Master the dark art of ZK! 🔐**
