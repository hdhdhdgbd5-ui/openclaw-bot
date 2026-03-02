# 🧠 Brain-Computer Interfaces (BCI)

**Direct mind-machine communication**

## What You Can Build

| Application | Description | Income Potential |
|-------------|-------------|------------------|
| **Neural Interfaces** | Control devices with thought | $100K-500K |
| **Neurofeedback** | Mental state training | $50K-200K |
| **Prosthetics** | Motor restoration | $200K-1M |
| **Communication** | ALS/locked-in support | $50K-200K |
| **Gaming/VR** | Mind-controlled experiences | $30K-150K |

---

## 📚 Learning Path

### Week 1: Neuroscience Basics
1. Brain anatomy
2. Neuron structure
3. Signal types (EEG, LFP, spikes)
4. Neural coding

### Week 2: Signal Processing
1. Filtering
2. Feature extraction
3. Spectral analysis
4. Artifact removal

### Week 3: Machine Learning
1. Classification
2. Decoding algorithms
3. Neural networks
4. Reinforcement learning

### Week 4: Implementation
1. OpenBCI SDK
2. Muse headband
3. Signal processing pipeline
4. Real-time control

---

## 💻 BCI Implementation

### EEG Signal Processing
```python
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq

class EEGProcessor:
    """
    Process EEG signals for BCI applications
    """
    
    def __init__(self, sample_rate=256):
        self.sample_rate = sample_rate
        self.n_channels = 8
        
    def bandpass_filter(self, data, lowcut, highcut, order=5):
        """
        Apply bandpass filter to EEG data
        """
        nyq = 0.5 * self.sample_rate
        low = lowcut / nyq
        high = highcut / nyq
        
        b, a = signal.butter(order, [low, high], btype='band')
        return signal.filtfilt(b, a, data)
    
    def extract_features(self, data):
        """
        Extract features from EEG:
        - Band powers (delta, alpha, beta, theta, gamma)
        - Spectral entropy
        - Statistical moments
        """
        features = []
        
        for channel in data:
            # Band powers
            bands = {
                'delta': (0.5, 4),
                'theta': (4, 8),
                'alpha': (8, 13),
                'beta': (13, 30),
                'gamma': (30, 100)
            }
            
            for band, (low, high) in bands.items():
                psd = self.compute_psd(channel, low, high)
                features.append(psd)
            
            # Spectral entropy
            entropy = self.spectral_entropy(channel)
            features.append(entropy)
            
            # Statistical features
            features.append(np.mean(channel))
            features.append(np.std(channel))
            features.append(np.var(channel))
        
        return np.array(features)
    
    def compute_psd(self, data, low, high):
        """Compute power in frequency band"""
        freqs, psd = signal.welch(data, self.sample_rate, nperseg=256)
        
        idx = np.logical_and(freqs >= low, freqs <= high)
        return np.sum(psd[idx])
    
    def spectral_entropy(self, data):
        """Compute spectral entropy"""
        freqs, psd = signal.welch(data, self.sample_rate)
        
        # Normalize PSD
        psd_norm = psd / np.sum(psd)
        
        # Compute entropy
        entropy = -np.sum(psd_norm * np.log2(psd_norm + 1e-10))
        return entropy
    
    def common_spatial_patterns(self, data, labels):
        """
        CSP for motor imagery classification
        Finds spatial filters that maximize variance difference
        """
        # Separate classes
        class1 = data[labels == 0]
        class2 = data[labels == 1]
        
        # Compute covariance matrices
        cov1 = np.cov(class1.T)
        cov2 = np.cov(class2.T)
        
        # Composite covariance
        cov = cov1 + cov2
        
        # Eigenvalue decomposition
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        
        # Sort by eigenvalue
        idx = eigenvalues.argsort()[::-1]
        eigenvectors = eigenvectors[:, idx]
        
        # Return spatial filters (first/last columns)
        n_filters = 2
        return np.hstack([eigenvectors[:, :n_filters], eigenvectors[:, -n_filters:]])
```

### Motor Imagery Classifier
```python
"""
Motor Imagery BCI: Classify left vs right hand movement
"""

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import StandardScaler

class MotorImageryBCI:
    """
    Motor imagery classification for BCI
    """
    
    def __init__(self):
        self.eeg_processor = EEGProcessor()
        self.classifier = LDA()
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Frequency bands for motor imagery
        self.bands = [(8, 12), (12, 16), (16, 24), (24, 32)]
    
    def preprocess(self, raw_eeg):
        """
        Preprocess raw EEG data
        """
        # Bandpass filter (0.5-40 Hz)
        filtered = self.eeg_processor.bandpass_filter(raw_eeg, 0.5, 40)
        
        # Extract features for each trial
        features = []
        
        for trial in filtered:
            trial_features = []
            
            for band in self.bands:
                # Band power for each channel
                for ch in range(trial.shape[0]):
                    psd = self.eeg_processor.compute_psd(trial[ch], band[0], band[1])
                    trial_features.append(psd)
            
            features.append(trial_features)
        
        return np.array(features)
    
    def train(self, eeg_data, labels):
        """
        Train the classifier
        """
        # Preprocess
        features = self.preprocess(eeg_data)
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Train classifier
        self.classifier.fit(features_scaled, labels)
        
        # Evaluate
        accuracy = self.classifier.score(features_scaled, labels)
        print(f"Training accuracy: {accuracy * 100:.2f}%")
        
        self.is_trained = True
    
    def predict(self, eeg_trial):
        """
        Predict motor imagery class
        """
        if not self.is_trained:
            raise RuntimeError("Classifier not trained")
        
        # Preprocess
        features = self.preprocess([eeg_trial])
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.classifier.predict(features_scaled)
        probabilities = self.classifier.predict_proba(features_scaled)
        
        return {
            'class': 'left' if prediction[0] == 0 else 'right',
            'confidence': max(probabilities[0])
        }

# Example usage
bci = MotorImageryBCI()
# bci.train(training_eeg, training_labels)
# result = bci.predict(test_eeg)
# print(f"Prediction: {result['class']}, Confidence: {result['confidence']:.2f}")
```

### Real-time Control Interface
```python
"""
Real-time BCI control for external devices
"""

import time
import threading
from collections import deque

class BCIInterface:
    """
    Real-time BCI interface
    """
    
    def __init__(self, buffer_size=256):
        self.buffer_size = buffer_size
        self.data_buffer = deque(maxlen=buffer_size)
        self.is_running = False
        self.classifier = MotorImageryBCI()
        
        # Control thresholds
        self.thresholds = {
            'left': 0.7,
            'right': 0.7,
            'relax': 0.6
        }
        
    def start_acquisition(self, device):
        """
        Start acquiring EEG data from device
        """
        self.is_running = True
        self.device = device
        
        # Start acquisition thread
        self.acquisition_thread = threading.Thread(target=self._acquire_data)
        self.acquisition_thread.start()
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_data)
        self.processing_thread.start()
    
    def _acquire_data(self):
        """
        Continuously acquire data from device
        """
        while self.is_running:
            # Read from device (example: OpenBCI)
            data = self.device.read_sample()
            self.data_buffer.append(data)
            time.sleep(1/256)  # Sample rate
    
    def _process_data(self):
        """
        Process data in real-time
        """
        buffer = []
        
        while self.is_running:
            # Accumulate buffer
            if len(self.data_buffer) >= 256:
                buffer = list(self.data_buffer)
                
                # Process
                result = self.classifier.predict(np.array(buffer))
                
                # Execute control based on prediction
                self._execute_control(result)
            
            time.sleep(0.01)
    
    def _execute_control(self, prediction):
        """
        Execute control commands based on prediction
        """
        if prediction['confidence'] > self.thresholds[prediction['class']]:
            command = prediction['class']
            print(f"Command: {command} (confidence: {prediction['confidence']:.2f})")
            
            # Map to control signals
            if command == 'left':
                self.move_left()
            elif command == 'right':
                self.move_right()
    
    def move_left(self):
        """Execute left movement"""
        pass
    
    def move_right(self):
        """Execute right movement"""
        pass
    
    def stop(self):
        """Stop BCI"""
        self.is_running = False
        self.acquisition_thread.join()
        self.processing_thread.join()
```

---

## 🛠️ Hardware

| Device | Channels | Type |
|--------|----------|------|
| **OpenBCI Cyton** | 8-32 | EEG |
| **Muse** | 4 | EEG |
| **g.tec** | 64-256 | EEG/ECoG |
| **Neuralink** | 1024 | Spikes |
| **Blackrock** | 96-128 | Spikes |

---

## 🎯 Next Steps

1. Get OpenBCI/Muse headset
2. Run motor imagery experiments
3. Build signal processing pipeline
4. Implement real-time control

**Mind meets machine! 🧠**
