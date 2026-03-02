# SECURITY MASTERCLASS
## Cryptography, Exploits & Advanced Security

---

## 1. MODERN CRYPTOGRAPHY

### 1.1 AES-GCM Implementation
```python
"""
AES-GCM (Galois/Counter Mode)
- Authenticated encryption
- 128/256 bit security
"""
import os

def gf_mult(a, b):
    """GF(2^128) multiplication"""
    result = 0
    while b:
        if b & 1:
            result ^= a
        a = (a << 1) ^ (0xE1 if a & 0x80 else 0)
        b >>= 1
    return result

def ghash(H, blocks):
    """GHASH function"""
    result = 0
    for block in blocks:
        result ^= int.from_bytes(block, 'big')
        result = gf_mult(result, int.from_bytes(H, 'big'))
    return result

def aes_gcm_encrypt(key, plaintext, nonce, aad=None):
    """
    AES-GCM Encryption
    key: 16 or 32 bytes
    plaintext: bytes
    nonce: 12 bytes (unique per encryption)
    aad: additional authenticated data (optional)
    """
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    
    # Counter starts at 1
    counter = 1
    
    # Encrypt
    cipher = Cipher(algorithms.AES(key), mode=modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    
    if aad:
        encryptor.authenticate_additional_data(aad)
    
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    
    return ciphertext, encryptor.tag

def aes_gcm_decrypt(key, ciphertext, nonce, tag, aad=None):
    """AES-GCM Decryption"""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    
    cipher = Cipher(algorithms.AES(key), mode=modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    
    if aad:
        decryptor.authenticate_additional_data(aad)
    
    return decryptor.update(ciphertext) + decryptor.finalize()
```

### 1.2 RSA with OAEP + PSS
```python
"""
RSA Cryptography with OAEP padding and PSS signatures
"""
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

def generate_rsa_keypair(key_size=4096):
    """Generate RSA key pair"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

def rsa_encrypt(public_key, plaintext):
    """RSA-OAEP encryption"""
    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def rsa_decrypt(private_key, ciphertext):
    """RSA-OAEP decryption"""
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext

def rsa_sign(private_key, message):
    """RSA-PSS signature"""
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def rsa_verify(public_key, message, signature):
    """RSA-PSS verification"""
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False
```

### 1.3 Elliptic Curve Cryptography
```python
"""
ECDSA and ECDH - Elliptic Curve Cryptography
"""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def generate_ec_keypair(curve=ec.SECP256R1()):
    """Generate ECDSA key pair"""
    private_key = ec.generate_private_key(curve, default_backend())
    public_key = private_key.public_key()
    return private_key, public_key

def ecdsa_sign(private_key, message):
    """ECDSA signing"""
    signature = private_key.sign(
        message,
        ec.ECDSA(hashes.SHA256())
    )
    return signature

def ecdsa_verify(public_key, message, signature):
    """ECDSA verification"""
    try:
        public_key.verify(
            signature,
            message,
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except:
        return False

def ecdh_key_exchange(private_key, public_key):
    """ECDH key exchange"""
    shared_key = private_key.exchange(public_key)
    return shared_key

# X25519 (Curve25519) - Modern elliptic curve
from cryptography.hazmat.primitives.asymmetric import x25519

def generate_x25519_keypair():
    """Generate X25519 key pair for key exchange"""
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

def x25519_key_exchange(private_key, public_key):
    """X25519 key exchange"""
    shared_key = private_key.exchange(public_key)
    return shared_key
```

### 1.4 SHA-3 and Keccak
```python
"""
SHA-3 and Keccak Implementation
"""
import os

def sha3_256(data):
    """SHA3-256 hash"""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    h = hashes.Hash(hashes.SHA3_256(), backend=default_backend())
    h.update(data)
    return h.finalize()

def sha3_512(data):
    """SHA3-512 hash"""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    h = hashes.Hash(hashes.SHA3_512(), backend=default_backend())
    h.update(data)
    return h.finalize()

def shake_256(data, output_length):
    """SHAKE256 - SHA-3 XOF"""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    h = hashes.Hash(hashes.SHAKE256(output_length), backend=default_backend())
    h.update(data)
    return h.finalize()
```

---

## 2. ZERO-KNOWLEDGE PROOFS

### 2.1 Schnorr Protocol
```python
"""
Schnorr Proof - Zero-Knowledge Proof of Knowledge
"""
import os
import hashlib

class SchnorrProver:
    def __init__(self, G, g, x):
        self.G = G  # Generator
        self.g = g  # Generator point
        self.x = x  # Private key
        self.p = G  # Prime order of group
    
    def prove(self, message):
        """Generate Schnorr proof"""
        # Random nonce
        k = int.from_bytes(os.urandom(32), 'big') % self.p
        R = self.g * k
        
        # Challenge
        h = int.from_bytes(hashlib.sha256(
            str(R).encode() + message
        ).digest(), 'big') % self.p
        
        # Response
        s = (k + h * self.x) % self.p
        
        return {'R': R, 's': s, 'challenge': h}

class SchnorrVerifier:
    def __init__(self, G, g, X):
        self.G = G
        self.g = g
        self.X = X  # Public key
        self.p = G
    
    def verify(self, message, proof):
        """Verify Schnorr proof"""
        R = proof['R']
        s = proof['s']
        h = proof['challenge']
        
        # Recompute challenge
        h_check = int.from_bytes(hashlib.sha256(
            str(R).encode() + message
        ).digest(), 'big') % self.p
        
        if h != h_check:
            return False
        
        # Verify: g^s = R * X^h
        left = self.g * s
        right = R + self.X * h
        
        return left == right
```

### 2.2 zk-SNARK (Simplified)
```python
"""
Simplified zk-SNARK implementation using Groth16
In practice, use libsnark or circom/snarkjs
"""
import os
import hashlib

class zkSNARK:
    """
    Zero-Knowledge Succinct Non-Interactive Argument of Knowledge
    
    This is a conceptual implementation.
    Production systems use:
    - circom for circuit compilation
    - snarkjs for proof generation/verification
    - libsnark for backend
    """
    
    @staticmethod
    def setup(circuit):
        """
        Trusted setup - generates proving/verification keys
        In practice: Powers of Tau ceremony
        """
        # Generate CRS (Common Reference String)
        tau = int.from_bytes(os.urandom(32), 'big')
        alpha = int.from_bytes(os.urandom(32), 'big')
        beta = int.from_bytes(os.urandom(32), 'big')
        gamma = int.from_bytes(os.urandom(32), 'big')
        delta = int.from_bytes(os.urandom(32), 'big')
        
        # These would be used to generate proving/verification keys
        return {
            'tau': tau,
            'alpha': alpha,
            'beta': beta,
            'gamma': gamma,
            'delta': delta
        }
    
    @staticmethod
    def prove(circuit, witness, pk):
        """Generate proof"""
        # In practice: Compute witness assignments
        # Evaluate constraints using witness
        # Create proof elements (A, B, C)
        
        proof = {
            'A': os.urandom(32).hex(),
            'B': os.urandom(64).hex(),
            'C': os.urandom(32).hex()
        }
        
        return proof
    
    @staticmethod
    def verify(circuit, proof, vk):
        """Verify proof"""
        # In practice: Pairing-based verification
        # e(A, B) = e(C, gamma) * product of public inputs
        return True  # Simplified
```

---

## 3. HASHING AND KEY DERIVATION

### 3.1 Argon2id
```python
"""
Argon2id - Winner of Password Hashing Competition
"""
import base64

def argon2_hash(password, salt=None, memory=65536, iterations=3, parallelism=4):
    """Argon2id password hashing"""
    import argon2
    from argon2 import PasswordHasher
    
    ph = PasswordHasher(
        time_cost=iterations,
        memory_cost=memory,
        parallelism=parallelism,
        hash_len=32,
        salt_len=16,
        type=argon2.Type.ID
    )
    
    hash = ph.hash(password)
    return hash

def argon2_verify(hash, password):
    """Verify Argon2 hash"""
    import argon2
    from argon2 import PasswordHasher
    
    ph = PasswordHasher()
    try:
        ph.verify(hash, password)
        return True
    except:
        return False
```

### 3.2 scrypt
```python
"""
scrypt - Memory-hard key derivation
"""
import os
import hashlib

def scrypt(password, salt=None, n=16384, r=8, p=1, dklen=64):
    """scrypt key derivation"""
    if salt is None:
        salt = os.urandom(16)
    
    # In practice, use hashlib.scrypt
    import hashlib
    key = hashlib.scrypt(
        password.encode() if isinstance(password, str) else password,
        salt=salt,
        n=n,
        r=r,
        p=p,
        dklen=dklen
    )
    
    return salt, key
```

### 3.3 HKDF
```python
"""
HKDF - HMAC-based Key Derivation Function
"""
import hmac
import hashlib

def hkdf_extract(salt, ikm):
    """HKDF-Extract"""
    if not salt:
        salt = b'\x00' * hashlib.sha256().block_size
    return hmac.new(salt, ikm, hashlib.sha256).digest()

def hkdf_expand(prk, info, length):
    """HKDF-Expand"""
    n = (length + hashlib.sha256().digest_size - 1) // hashlib.sha256().digest_size
    okm = b''
    t = b''
    
    for i in range(1, n + 1):
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
        okm += t
    
    return okm[:length]

def hkdf(password, salt, info, length):
    """Full HKDF"""
    prk = hkdf_extract(salt, password)
    return hkdf_expand(prk, info, length)
```

---

## 4. SECURE PROTOCOLS

### 4.1 TLS 1.3 Handshake
```python
"""
TLS 1.3 Handshake Protocol
"""
import os
import hashlib
import hmac

class TLS13Handshake:
    def __init__(self):
        self.cipher_suites = [
            'TLS_AES_256_GCM_SHA384',
            'TLS_CHACHA20_POLY1305_SHA256',
            'TLS_AES_128_GCM_SHA256'
        ]
    
    def client_hello(self, client_random, supported_versions, key_share):
        """ClientHello message"""
        return {
            'client_random': client_random,
            'version': 'TLS 1.3',
            'supported_versions': supported_versions,
            'key_share': key_share,
            'cipher_suites': self.cipher_suites
        }
    
    def server_hello(self, server_random, selected_version, key_share):
        """ServerHello message"""
        return {
            'server_random': server_random,
            'version': 'TLS 1.3',
            'selected_version': selected_version,
            'key_share': key_share
        }
    
    def derive_keys(self, client_random, server_random, 
                   shared_secret, handshake_transcript):
        """Key derivation using HKDF"""
        # Early secrets
        empty_hash = hashlib.sha256().digest()
        
        # Derived secrets
        derived = hkdf_expand(
            hkdf_extract(b' tls13 derived', empty_hash),
            b'', 32
        )
        
        # Handshake secret
        handshake_secret = hkdf_extract(
            derived,
            shared_secret
        )
        
        # Traffic secrets
        client_handshake = hkdf_expand(
            hkdf_extract(
                hkdf_expand(
                    hkdf_extract(b'tls13 c hs traffic', handshake_secret),
                    handshake_transcript, 32
                ),
                b'', 32
            ),
            b'tls13 ap traffic', 32
        )
        
        return {
            'client_handshake': client_handshake,
            'server_handshake': None  # Similar derivation
        }
```

### 4.2 OAuth 2.0 + PKCE
```python
"""
OAuth 2.0 with PKCE
"""
import os
import hashlib
import base64
import secrets

class OAuth2PKCE:
    def __init__(self, client_id, redirect_uri, authorization_endpoint, token_endpoint):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.auth_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
    
    def generate_code_verifier(self):
        """Generate PKCE code verifier"""
        return base64.urlsafe_b64encode(
            os.urandom(32)
        ).rstrip(b'=').decode()
    
    def generate_code_challenge(self, verifier):
        """Generate PKCE code challenge (S256)"""
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
    
    def get_authorization_url(self, state, code_verifier):
        """Build authorization URL"""
        code_challenge = self.generate_code_challenge(code_verifier)
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'openid profile email',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        # Build URL
        from urllib.parse import urlencode
        return f"{self.auth_endpoint}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code, code_verifier):
        """Exchange authorization code for tokens"""
        # In practice, make POST request to token_endpoint
        return {
            'access_token': secrets.token_urlsafe(32),
            'refresh_token': secrets.token_urlsafe(32),
            'token_type': 'Bearer',
            'expires_in': 3600
        }
```

---

## 5. SECURITY VULNERABILITIES

### 5.1 SQL Injection Prevention
```python
"""
SQL Injection Prevention
"""
import sqlite3

# VULNERABLE - Never do this!
def vulnerable_login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # DANGER: SQL Injection!
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    return cursor.fetchone()

# SECURE - Parameterized queries
def secure_login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # SAFE: Parameterized query
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    return cursor.fetchone()

# SECURE - ORM with parameterized queries
def orm_login(username, password):
    from sqlalchemy import text
    conn = sqlite3.connect('users.db')
    query = text("SELECT * FROM users WHERE username = :user AND password = :pass")
    result = conn.execute(query, {'user': username, 'pass': password})
    return result.fetchone()
```

### 5.2 XSS Prevention
```python
"""
Cross-Site Scripting (XSS) Prevention
"""
import html

# VULNERABLE
def vulnerable_render(user_input):
    return f"<div>{user_input}</div>"

# SECURE - HTML escaping
def secure_render(user_input):
    escaped = html.escape(user_input)
    return f"<div>{escaped}</div>"

# SECURE - Content Security Policy
def get_csp_header():
    """Content Security Policy header"""
    return {
        'Content-Security-Policy': 
            "default-src 'self'; "
            "script-src 'self' 'nonce-{nonce}'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' https://api.example.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
    }

# SECURE - DOMPurify equivalent
def sanitize_html(dirty_html, allowed_tags=None):
    """HTML sanitization"""
    if allowed_tags is None:
        allowed_tags = ['p', 'br', 'b', 'i', 'em', 'strong', 'a', 'ul', 'ol', 'li']
    
    # Simple sanitization (in production, use bleach or DOMPurify)
    import re
    clean = dirty_html
    
    # Remove script tags
    clean = re.sub(r'<script[^>]*>.*?</script>', '', clean, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove on* event handlers
    clean = re.sub(r'\s*on\w+\s*=\s*["\'].*?["\']', '', clean, flags=re.IGNORECASE)
    
    return clean
```

### 5.3 CSRF Protection
```python
"""
CSRF Token Implementation
"""
import os
import hmac
import hashlib
import base64
import time

class CSRFProtection:
    def __init__(self, secret_key):
        self.secret = secret_key.encode()
    
    def generate_token(self, user_id=None):
        """Generate CSRF token"""
        # Create random bytes
        random_bytes = os.urandom(32)
        
        # Create HMAC
        message = f"{user_id or ''}{time.time()}".encode()
        signature = hmac.new(self.secret, message, hashlib.sha256).digest()
        
        # Combine and encode
        token = base64.urlsafe_b64encode(random_bytes + signature).decode()
        return token
    
    def validate_token(self, token, user_id=None):
        """Validate CSRF token"""
        try:
            decoded = base64.urlsafe_b64decode(token.encode())
            random_bytes = decoded[:32]
            signature = decoded[32:]
            
            # Verify signature
            message = f"{user_id or ''}{time.time()}".encode()
            expected = hmac.new(self.secret, message, hashlib.sha256).digest()
            
            return hmac.compare_digest(signature, expected)
        except:
            return False
```

### 5.4 Password Storage Best Practices
```python
"""
Secure Password Storage
"""
import os
import hashlib
import hmac

# NEVER store plaintext passwords!
# ALWAYS use proper password hashing

def hash_password(password, salt=None):
    """Argon2id (recommended) or bcrypt"""
    # Using PBKDF2-HMAC-SHA256 as fallback
    if salt is None:
        salt = os.urandom(32)
    
    # PBKDF2 with high iterations
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        iterations=600000,  # Minimum recommended
        dklen=32
    )
    
    return salt + key  # Store salt with hash

def verify_password(password, stored):
    """Verify password against stored hash"""
    salt = stored[:32]
    stored_hash = stored[32:]
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        iterations=600000,
        dklen=32
    )
    
    return hmac.compare_digest(key, stored_hash)

# Secure password generation
def generate_secure_password(length=16):
    """Generate cryptographically secure password"""
    import string
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(os.urandom(length).translate(
        {i: ord(chars[i % len(chars)]) for i in range(length)}
    ))
```

---

## 6. THREAT MODELS

### 6.1 Threat Modeling Framework
```python
"""
STRIDE Threat Model
"""
class ThreatModel:
    """
    STRIDE:
    - Spoofing
    - Tampering
    - Repudiation
    - Information Disclosure
    - Denial of Service
    - Elevation of Privilege
    """
    
    @staticmethod
    def identify_spoofing_threats():
        return [
            "User impersonation",
            "Session hijacking",
            "Man-in-the-middle attacks",
            "DNS spoofing"
        ]
    
    @staticmethod
    def identify_tampering_threats():
        return [
            "Data in transit modification",
            "Data at rest modification",
            "Code injection",
            "Memory tampering"
        ]
    
    @staticmethod
    def identify_repudiation_threats():
        return [
            "Log tampering",
            "Missing audit trails",
            "Non-repudiation of actions"
        ]
    
    @staticmethod
    def identify_disclosure_threats():
        return [
            "Data breach",
            "Information leakage",
            "Side-channel attacks",
            "Insecure logging"
        ]
    
    @staticmethod
    def identify_dos_threats():
        return [
            "DDoS attacks",
            "Resource exhaustion",
            "Service degradation"
        ]
    
    @staticmethod
    def identify_privilege_threats():
        return [
            "Privilege escalation",
            "Broken access control",
            "Insecure direct object references"
        ]

# MITRE ATT&CK Mapping
class ATTACKFramework:
    """MITRE ATT&CK Tactics"""
    
    TACTICS = [
        'TA0001 - Initial Access',
        'TA0002 - Execution',
        'TA0003 - Persistence',
        'TA0004 - Privilege Escalation',
        'TA0005 - Defense Evasion',
        'TA0006 - Credential Access',
        'TA0007 - Discovery',
        'TA0008 - Lateral Movement',
        'TA0009 - Collection',
        'TA0010 - Exfiltration',
        'TA0011 - Command and Control'
    ]
```

---

## 7. CRYPTOGRAPHIC AUDITING

### 7.1 Cryptanalysis Tools
```python
"""
Cryptographic Best Practices Checklist
"""
CRYPTO_CHECKLIST = {
    "symmetric_encryption": {
        "recommended": ["AES-256-GCM", "ChaCha20-Poly1305"],
        "deprecated": ["DES", "3DES", "RC4", "AES-ECB"],
        "notes": "Always use authenticated encryption"
    },
    "asymmetric_encryption": {
        "recommended": ["RSA-4096", "ECIES", "ECIES"],
        "deprecated": ["RSA-1024", "RSA-2048 (deprecated)"],
        "notes": "Use OAEP padding, not PKCS1v15"
    },
    "signatures": {
        "recommended": ["ECDSA (P-384)", "Ed25519", "RSA-PSS"],
        "deprecated": ["DSA", "RSA-PKCS1v15"],
        "notes": "Prefer deterministic signatures"
    },
    "hashing": {
        "recommended": ["SHA-256", "SHA-384", "SHA-512", "BLAKE3"],
        "deprecated": ["MD5", "SHA-1"],
        "notes": "SHA-3 is also recommended"
    },
    "key_derivation": {
        "recommended": ["Argon2id", "bcrypt", "scrypt", "PBKDF2 (high iterations)"],
        "deprecated": ["PBKDF2 (low iterations)", "MD5-based KDF"],
        "notes": "Argon2id preferred for passwords"
    },
    "key_exchange": {
        "recommended": ["X25519", "ECDH (P-384)"],
        "deprecated": ["DH-1024", "ECDH (P-256)"],
        "notes": "X25519 preferred for performance"
    },
    "randomness": {
        "recommended": ["os.urandom", "secrets module"],
        "deprecated": ["random module", " Mersenne Twister"],
        "notes": "NEVER use deterministic RNG for crypto"
    },
    "tls_versions": {
        "recommended": ["TLS 1.3"],
        "deprecated": ["TLS 1.0", "TLS 1.1", "SSL"],
        "notes": "Disable TLS 1.2 if possible"
    }
}

def audit_crypto_usage(algorithm, mode=None):
    """Audit cryptographic algorithm usage"""
    for category, info in CRYPTO_CHECKLIST.items():
        if algorithm in info.get("deprecated", []):
            return {
                "status": "DEPRECATED",
                "message": f"{algorithm} is deprecated. {info['notes']}",
                "recommendations": info.get("recommended", [])
            }
        elif algorithm in info.get("recommended", []):
            return {
                "status": "RECOMMENDED",
                "message": info['notes']
            }
    return {"status": "UNKNOWN", "message": "Algorithm not in database"}
```

---

*End of Security Masterclass*
