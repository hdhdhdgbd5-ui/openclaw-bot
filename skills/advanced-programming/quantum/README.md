# ⚛️ Quantum Computing

**Build the future of computation**

## What You Can Build

| Application | Description | Income Potential |
|-------------|-------------|------------------|
| **Quantum Simulators** | Emulate quantum systems | $50K-200K |
| **Cryptanalysis** | Post-quantum crypto | $100K-500K |
| **Optimization** | QAOA, VQE algorithms | $80K-300K |
| **ML/AI** | Quantum machine learning | $100K-400K |
| **Quantum Cloud** | QaaS platforms | $200K-1M |

---

## 📚 Learning Path

### Week 1: Quantum Basics
1. Linear algebra refresher
2. Qubits and states
3. Quantum gates
4. Measurements

### Week 2: Quantum Algorithms
1. Deutsch-Jozsa
2. Grover's search
3. Shor's factoring
4. Quantum Fourier Transform

### Week 3: Implementation
1. Qiskit
2. Cirq
3. Pennylane
4. Error correction

### Week 4: Applications
1. VQE for chemistry
2. QAOA for optimization
3. Quantum ML
4. Cryptography

---

## 💻 Quantum Computing with Qiskit

### Basic Quantum Circuit
```python
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

# Create a quantum circuit with 2 qubits
qc = QuantumCircuit(2)

# Apply Hadamard gate on qubit 0
qc.h(0)

# Apply CNOT gate (control: 0, target: 1)
qc.cx(0, 1)

# Apply measurement
qc.measure_all()

# Simulate
simulator = AerSimulator()
result = simulator.run(qc).result()
counts = result.get_counts()
print(f"Counts: {counts}")

# Statevector (before measurement)
sv = Statevector.from_instruction(qc)
print(f"Statevector: {sv.data}")
```

### Grover's Search Algorithm
```python
"""
Grover's algorithm: Search unsorted database in O(sqrt(N))
"""

def grovers_oracle(qc, target_state):
    """Mark the target state"""
    # Apply X gates to flip bits where target has 0
    for i, bit in enumerate(target_state):
        if bit == '0':
            qc.x(i)
    
    # Multi-controlled Z
    qc.h(len(target_state) - 1)
    qc.mcx(list(range(len(target_state) - 1)), len(target_state) - 1)
    qc.h(len(target_state) - 1)
    
    # Undo the X gates
    for i, bit in enumerate(target_state):
        if bit == '0':
            qc.x(i)

def grovers_diffuser(qc, n_qubits):
    """Amplify the probability of marked states"""
    # Apply Hadamard to all
    for i in range(n_qubits):
        qc.h(i)
    
    # Apply X to all
    for i in range(n_qubits):
        qc.x(i)
    
    # Multi-controlled Z
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)
    
    # Undo X and H
    for i in range(n_qubits):
        qc.x(i)
        qc.h(i)

def grovers_search(target_state, iterations=None):
    """Complete Grover's algorithm"""
    n_qubits = len(target_state)
    
    if iterations is None:
        iterations = int((3.14159 / 4) * (2 ** (n_qubits / 2)))
    
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Initial superposition
    for i in range(n_qubits):
        qc.h(i)
    
    # Grover iterations
    for _ in range(iterations):
        grovers_oracle(qc, target_state)
        grovers_diffuser(qc, n_qubits)
    
    # Measure
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc

# Example: Search for |101⟩
circuit = grovers_search('101')
print(circuit)
```

### Shor's Factoring Algorithm
```python
"""
Shor's algorithm: Factor N in polynomial time
"""

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
import math

def shor_circuit(N, a):
    """
    Shor's algorithm for factoring N
    a: random base such that gcd(a, N) = 1
    """
    # Number of bits for N
    n_bits = N.bit_length()
    
    # Use 2 * n_bits for precision
    n_qubits = 2 * n_bits
    
    qc = QuantumCircuit(n_qubits, n_bits)
    
    # Initialize first n_bits to superposition
    for i in range(n_bits):
        qc.h(i)
    
    # Apply modular exponentiation: |x⟩ → |a^x mod N⟩
    # This is the hard part - requires controlled rotations
    # Simplified version:
    
    # QFT on counting qubits
    qc.compose(QFT(n_bits, do_swaps=False), range(n_bits), inplace=True)
    
    # Inverse QFT
    qc.compose(QFT(n_bits, do_swaps=False).inverse(), range(n_bits), inplace=True)
    
    # Measure
    qc.measure(range(n_bits), range(n_bits))
    
    return qc

def find_period(a, N, shots=1000):
    """
    Find period of a mod N using Shor
    """
    # This is a simplified version
    # Real implementation needs controlled modular exponentiation
    
    n_bits = N.bit_length()
    qc = QuantumCircuit(2 * n_bits, n_bits)
    
    # Superposition
    for i in range(n_bits):
        qc.h(i)
    
    # Apply modular exponentiation
    # For demonstration, use simpler approach
    x = 1
    for j in range(2**n_bits):
        x = (x * a) % N
    
    return x

def classical_period_finding(a, N):
    """
    Classical period finding (for comparison)
    """
    if math.gcd(a, N) != 1:
        return None
    
    x = 1
    for i in range(1, N + 1):
        x = (x * a) % N
        if x == 1:
            return i
    
    return N
```

---

## 🧪 Variational Quantum Eigensolver (VQE)

```python
"""
VQE: Find ground state energy of molecule
"""

from qiskit import QuantumCircuit
from qiskit.algorithms import VQE
from qiskit.algorithms.optimizers import SPSA
from qiskit.circuit.library import EfficientSU2
from qiskit.opflow import X, Y, Z, I

def create_hamiltonian():
    """
    Create molecular Hamiltonian for H2
    H = -1.0413*I + 0.3979*Z + -0.3979*Z + 0.1812*ZZ
    """
    H = (
        -1.0413 * I ^ I ^
        0.3979 * Z ^ I ^
        -0.3979 * I ^ Z ^
        0.1812 * Z ^ Z
    )
    return H

def vqe_example():
    """
    Run VQE to find ground state
    """
    H = create_hamiltonian()
    
    # Variational form
    ansatz = EfficientSU2(2, reps=1)
    
    # Optimizer
    optimizer = SPSA(maxiter=100)
    
    # Run VQE
    vqe = VQE(ansatz, optimizer)
    result = vqe.compute_minimum_eigenvalue(H)
    
    print(f"Optimal parameters: {result.optimal_parameters}")
    print(f"Ground state energy: {result.optimal_value}")
    print(f"Eigenvalue: {result.eigenvalue}")

# Run
vqe_example()
```

---

## 🛠️ Tools

| Tool | Purpose |
|------|---------|
| **Qiskit** | IBM quantum SDK |
| **Cirq** | Google quantum |
| **Pennylane** | Quantum ML |
| **Braket** | AWS quantum |
| **Azure Quantum** | Microsoft quantum |

---

## 🎯 Next Steps

1. Complete Qiskit tutorials
2. Read "Quantum Computation and Quantum Information"
3. Implement quantum error correction
4. Build quantum ML model

**The future is quantum! ⚛️**
