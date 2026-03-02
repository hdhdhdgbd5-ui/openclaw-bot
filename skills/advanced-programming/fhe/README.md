# 🔒 Fully Homomorphic Encryption (FHE)

**Compute on encrypted data - the holy grail of privacy**

## What You Can Build

| Application | Description | Income Potential |
|-------------|-------------|------------------|
| **Encrypted Cloud Computing** | Process data without decryption | $50K-200K/project |
| **Private ML Inference** | Query AI without revealing input | $30K-150K/project |
| **Encrypted Databases** | SQL on ciphertext | $20K-100K/project |
| **Private Set Intersection** | Find common elements secretly | $15K-50K/project |
| **Secure Multi-Party Computation** | Collaborative computing | $30K-200K/project |
| **Privacy-Preserving Analytics** | Analytics on sensitive data | $20K-100K/project |

---

## 📚 Learning Path

### Week 1: Mathematical Foundations
1. Modular arithmetic
2. Lattice-based cryptography
3. Ring Learning With Errors (RLWE)
4. Number Theoretic Transform (NTT)

### Week 2: FHE Schemes
1. Gentry's original scheme
2. Brakerski/Fan-Vercauteren (BFV)
3. Cheon-Kim-Kim-Song (CKKS)
4. TFHE (Toroidal FHE)

### Week 3: Implementation
1. SEAL library
2. PALISADE library
3. OpenFHE
4. Concrete (Zama)

### Week 4: Applications
1. Encrypted neural networks
2. Private queries
3. Secure auctions
4. Federated learning

---

## 🧮 Mathematical Foundation

### Lattice-Based Cryptography
```python
"""
FHE is built on lattice problems - computationally hard even for quantum computers
"""

import numpy as np

class LatticeProblem:
    """
    Shortest Vector Problem (SVP): Find shortest non-zero vector in lattice
    Learning With Errors (LWE): Find secret s given (A, b = As + e)
    Ring-LWE (RLWE): LWE in polynomial rings
    """
    
    @staticmethod
    def generate_lwe_sample(n, q, stddev=3.19):
        """
        Generate LWE sample: (a, b = a·s + e) where:
        - a: random vector
        - s: secret vector (small)
        - e: error vector (small gaussian)
        """
        # Random matrix A
        A = np.random.randint(0, q, (n, n))
        
        # Secret vector (small)
        s = np.random.randint(-2, 3, n)
        
        # Error vector (gaussian)
        e = np.round(np.random.normal(0, stddev, n)).astype(int)
        
        # b = A·s + e (mod q)
        b = (A @ s + e) % q
        
        return A, b, s
    
    @staticmethod
    def generate_rlwe_sample(n, q):
        """
        RLWE: Work in polynomial ring R = Z_q[x]/(x^n + 1)
        More efficient than LWE
        """
        # Random polynomial a(x)
        a = np.random.randint(0, q, n)
        
        # Secret polynomial s(x)
        s = np.random.randint(-2, 3, n)
        
        # Error polynomial
        e = np.round(np.random.normal(0, 3.19, n)).astype(int)
        
        # b(x) = a(x) · s(x) + e(x) (mod q, x^n + 1)
        # Polynomial multiplication (with modular reduction)
        b = np.convolve(a, s) % q
        b = (b + e) % q
        
        # Reduce degree if needed
        b = b[:n]
        
        return a, b, s


# Number Theoretic Transform for fast polynomial multiplication
def ntt(poly, primitive_root, q):
    """
    NTT: Number Theoretic Transform
    Fast polynomial multiplication in O(n log n)
    """
    n = len(poly)
    if n == 1:
        return poly
    
    # Bit reversal
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        
        if i < j:
            poly[i], poly[j] = poly[j], poly[i]
    
    # Cooley-Tukey butterfly
    length = 2
   :
        wlen = pow(primitive while length <= n_root, (q - 1) // length, q)
        for i in range(0, n, length):
            w = 1
            for j in range(i, i + length // 2):
                u = poly[j]
                v = poly[j + length // 2] * w % q
                poly[j] = (u + v) % q
                poly[j + length // 2] = (u - v) % q
                w = w * wlen % q
        length <<= 1
    
    return poly
```

---

## 🔧 FHE Library Implementation

### BFV Scheme (Brakerski/Fan-Vercauteren)
```python
"""
Simplified BFV scheme implementation
"""

import numpy as np

class BFV:
    def __init__(self, poly_degree=4096, plain_modulus=256, cipher_modulus=2**60):
        self.n = poly_degree
        self.t = plain_modulus
        self.q = cipher_modulus
        
    def keygen(self):
        """Generate public and secret keys"""
        # Secret key: small polynomial
        sk = np.random.randint(-1, 2, self.n)
        
        # Public key: pk = (-a·s + e, a) where a random, e small error
        a = np.random.randint(0, self.q, self.n)
        e = np.random.randint(-3, 4, self.n)
        
        # In practice: use RLWE sample generation
        # Simplified here
        pk = (a, np.convolve(a, sk) % self.q + e)
        
        # Evaluation keys for relinearization
        evk = self._generate_evaluation_key(sk)
        
        return {'sk': sk, 'pk': pk, 'evk': evk}
    
    def _generate_evaluation_key(self, sk):
        """Generate keys for homomorphic operations"""
        # For relinearization (turn 2-element ciphertext into 1)
        # Large LWE sample: (a, a·s + e + β·t)
        return {'rlk': np.random.randint(0, self.q, (2, self.n))}
    
    def encrypt(self, pk, plaintext):
        """Encrypt plaintext (polynomial)"""
        # Convert plaintext to polynomial
        m = self._encode_plaintext(plaintext)
        
        # Sample random u, e1, e2
        u = np.random.randint(0, 2, self.n)
        e1 = np.random.randint(-3, 4, self.n)
        e2 = np.random.randint(-3, 4, self.n)
        
        # c0 = pk[0]·u + e1 + Δ·m
        # c1 = pk[1]·u + e2
        delta = self.q // self.t
        c0 = (np.convolve(pk[0], u) + e1 + delta * m) % self.q
        c1 = (np.convolve(pk[1], u) + e2) % self.q
        
        return (c0, c1)
    
    def _encode_plaintext(self, message):
        """Encode integer message as polynomial"""
        poly = np.zeros(self.n, dtype=int)
        # Simple encoding: fill first slots with message
        for i, m in enumerate(message):
            poly[i] = m % self.t
        return poly
    
    def decrypt(self, sk, ciphertext):
        """Decrypt ciphertext"""
        c0, c1 = ciphertext
        
        # m = ⌊(c0 + c1·s) / Δ⌋ (mod t)
        delta = self.q // self.t
        m = (c0 + np.convolve(c1, sk)) % self.q
        m = (m * (self.t // self.q + 1)) % self.t  # Scale up for rounding
        
        return m
    
    def add(self, ct1, ct2):
        """Homomorphic addition"""
        return ((ct1[0] + ct2[0]) % self.q, (ct1[1] + ct2[1]) % self.q)
    
    def multiply(self, ct1, ct2, evk):
        """Homomorphic multiplication with relinearization"""
        c0_1, c1_1 = ct1
        c0_2, c1_2 = ct2
        
        # Polynomial multiplication
        c0 = np.convolve(c0_1, c0_2) % self.q
        c1 = (np.convolve(c0_1, c2_1) + np.convolve(c0_2, c1_1)) % self.q
        c2 = np.convolve(c1_1, c1_2) % self.q
        
        # Relinearization (simplified)
        # In practice: use evaluation keys to reduce from 2 to 1 ciphertext
        
        return (c0 % self.q, c1 % self.q)


# Example usage
bfv = BFV()
keys = bfv.keygen()

# Encrypt
message = [10, 20, 30, 0, 0, 0, 0, 0]
ct1 = bfv.encrypt(keys['pk'], message)
ct2 = bfv.encrypt(keys['pk'], [5, 5, 5, 0, 0, 0, 0, 0])

# Homomorphic addition
ct_sum = bfv.add(ct1, ct2)
result = bfv.decrypt(keys['sk'], ct_sum)
print("Sum:", result[:4])  # Should be [15, 25, 35, 0]
```

---

## 🧠 Encrypted Neural Network Inference

### Using Concrete (Zama's FHE Library)
```python
"""
Privacy-preserving ML: Run neural network on encrypted data
Example: Encrypted image classification
"""

# This is conceptual - actual implementation uses Concrete-ML

from concrete import fhe
import numpy as np

@fhe.compile({"x": "encrypted"})
def encrypted_inference(x):
    """
    Neural network that runs on encrypted inputs
    Input x: encrypted image pixels
    Output: encrypted class probabilities
    """
    # Layer 1: Conv + ReLU
    # In FHE, use table lookup for ReLU (approximation)
    x = x @ fhe.ones(256) + fhe.zeros(256)
    x = fhe.lookup(x, table=np.array([0, 1, 2, 3]))  # ReLU approx
    
    # Layer 2: Dense
    x = x @ fhe.ones(128) + fhe.zeros(128)
    x = fhe.lookup(x, table=np.array(range(128)))  # ReLU
    
    # Output: softmax approximation
    x = fhe.lookup(x, table=np.exp(np.arange(10)))
    
    return x


# Usage (in production would use actual FHE backend)
def private_classification(model, encrypted_image):
    """
    Classify image without seeing it
    """
    # Client sends encrypted image
    encrypted_prediction = model.encrypt(encrypted_image)
    
    # Server runs inference on encrypted data
    result = model.run(encrypted_prediction)
    
    # Client decrypts result to see prediction
    return result


# Alternative: Using SEAL directly
class EncryptedML:
    """
    Encrypted ML using Microsoft SEAL
    """
    
    def __init__(self):
        # Initialize SEAL context
        self.params = {
            'poly_modulus_degree': 4096,
            'coeff_modulus': [0x1FFFFFFFFFFFFF, 0x1FFFFFFFFFFFFF],
            'plain_modulus': 256
        }
        # In practice: use seal_py bindings
    
    def encrypt_weights(self, weights):
        """Encrypt model weights"""
        return weights  # Simplified
    
    def forward(self, encrypted_input, weights):
        """
        Forward pass on encrypted data
        """
        # Convolution = polynomial multiplication
        # Activation = table lookup (CMUX operation)
        
        # Simple: encrypted dot product
        result = 0
        for i in range(len(encrypted_input)):
            result = result + encrypted_input[i] * weights[i]
        
        return result
```

---

## 🔐 Private Set Intersection

```python
"""
Private Set Intersection (PSI)
Find common elements between two parties without revealing sets
"""

class PrivateSetIntersection:
    """
    FHE-based PSI protocol
    """
    
    def __init__(self, fhe):
        self.fhe = fhe
        self.keys = fhe.keygen()
    
    def client_setup(self, client_set):
        """
        Client encrypts their set and sends to server
        """
        # Hash elements to polynomial points
        hashed = [self._hash_to_int(x) for x in client_set]
        
        # Encrypt each element
        encrypted_set = [self.fhe.encrypt(self.keys['pk'], [h]) 
                        for h in hashed]
        
        return encrypted_set
    
    def server_process(self, encrypted_client_set, server_set):
        """
        Server checks intersection with their set
        """
        results = []
        
        for h_server in server_set:
            # Compute: product of (enc_client - h_server)
            # If element matches, result = 0, else non-zero
            
            intersection = None
            for enc_client in encrypted_client_set:
                diff = self.fhe.subtract(enc_client, h_server)
                
                if intersection is None:
                    intersection = diff
                else:
                    intersection = self.fhe.multiply(intersection, diff)
            
            results.append(intersection)
        
        return results
    
    def client_decode(self, results, threshold=100):
        """
        Client decrypts results to find intersection
        Non-zero values indicate no match
        """
        intersection = []
        
        for i, result in enumerate(results):
            decrypted = self.fhe.decrypt(self.keys['sk'], result)
            
            if abs(decrypted[0]) < threshold:
                intersection.append(i)
        
        return intersection
    
    @staticmethod
    def _hash_to_int(x):
        """Hash to integer for polynomial encoding"""
        import hashlib
        return int(hashlib.sha256(str(x).encode()).hexdigest(), 16)
```

---

## 🛠️ Libraries & Tools

| Library | Language | Status |
|---------|----------|--------|
| **Microsoft SEAL** | C++, Python | Mature |
| **PALISADE** | C++ | Mature |
| **OpenFHE** | C++, Python | Mature |
| **Concrete** (Zama) | Rust, Python | Active |
| **HEAAN** | C++ | Research |
| **TFHE** | C++ | Fast bootstrapping |

---

## 📖 Exercises

### Exercise 1: Encrypted Calculator
Build service that:
- Accepts encrypted numbers
- Performs +, -, × operations
- Returns encrypted result

### Exercise 2: Private Voting
Build system where:
- Votes are encrypted
- Only final tally is decrypted
- Individual votes never revealed

### Exercise 3: Encrypted Search
Build search that:
- Searches encrypted database
- Returns encrypted results
- Server never sees query or results

---

## 🎯 Next Steps

1. ✅ Experiment with SEAL or Concrete
2. 📚 Read FHE papers (Gentry, Brakerski, Cheon)
3. 🔒 Study security proofs
4. 📖 Read "A Pragmatic Introduction to FHE"
5. 🏆 Build real privacy products

**The future is encrypted! 🔐**
