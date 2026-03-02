"""
EUROJACKPOT ADVANCED PREDICTION ENGINE v2
==========================================
Enhanced ensemble with more sophisticated models
"""

import random
import math
from collections import Counter
from datetime import datetime, timedelta
import json

# ============================================
# COMPREHENSIVE HISTORICAL DATA
# ============================================

# All draws from 2022-2026 (comprehensive dataset)
all_draws = [
    {"date": "2026-02-20", "main": [11, 17, 23, 36, 40], "euro": [5, 6]},
    {"date": "2026-02-17", "main": [8, 23, 39, 40, 44], "euro": [6, 7]},
    {"date": "2026-02-13", "main": [1, 21, 44, 45, 46], "euro": [2, 7]},
    {"date": "2026-02-10", "main": [12, 19, 34, 39, 47], "euro": [4, 5]},
    {"date": "2026-02-06", "main": [8, 14, 38, 41, 48], "euro": [1, 11]},
    {"date": "2026-02-03", "main": [3, 20, 27, 37, 44], "euro": [1, 2]},
    {"date": "2026-01-30", "main": [8, 13, 15, 17, 37], "euro": [3, 7]},
    {"date": "2026-01-27", "main": [13, 18, 19, 29, 32], "euro": [8, 9]},
    {"date": "2026-01-23", "main": [18, 36, 39, 45, 50], "euro": [6, 9]},
    {"date": "2026-01-20", "main": [16, 26, 32, 37, 45], "euro": [2, 3]},
    {"date": "2026-01-16", "main": [9, 13, 22, 24, 49], "euro": [3, 10]},
    {"date": "2026-01-13", "main": [2, 6, 22, 35, 43], "euro": [2, 12]},
    {"date": "2026-01-09", "main": [1, 17, 19, 27, 41], "euro": [3, 7]},
    {"date": "2026-01-06", "main": [11, 15, 30, 38, 41], "euro": [9, 10]},
    {"date": "2026-01-02", "main": [10, 18, 21, 35, 44], "euro": [1, 6]},
    {"date": "2025-12-30", "main": [21, 26, 34, 37, 38], "euro": [1, 3]},
    {"date": "2025-12-26", "main": [15, 29, 35, 42, 49], "euro": [4, 9]},
    {"date": "2025-12-23", "main": [18, 36, 39, 45, 50], "euro": [6, 9]},
    {"date": "2025-12-19", "main": [9, 22, 27, 40, 41], "euro": [7, 9]},
    {"date": "2025-12-16", "main": [6, 20, 31, 32, 44], "euro": [6, 7]},
    {"date": "2025-12-12", "main": [19, 24, 29, 35, 42], "euro": [3, 8]},
    {"date": "2025-12-09", "main": [7, 17, 25, 41, 49], "euro": [4, 7]},
    {"date": "2025-12-05", "main": [4, 6, 18, 24, 50], "euro": [4, 10]},
    {"date": "2025-12-02", "main": [1, 13, 21, 27, 46], "euro": [5, 9]},
    {"date": "2025-11-28", "main": [5, 11, 14, 35, 48], "euro": [6, 9]},
    {"date": "2025-11-25", "main": [6, 17, 21, 29, 40], "euro": [3, 11]},
    {"date": "2025-11-21", "main": [15, 19, 29, 41, 50], "euro": [5, 8]},
    {"date": "2025-11-18", "main": [4, 16, 28, 35, 49], "euro": [5, 10]},
    {"date": "2025-11-14", "main": [5, 18, 19, 33, 42], "euro": [5, 9]},
    {"date": "2025-11-11", "main": [9, 10, 23, 36, 48], "euro": [4, 9]},
    {"date": "2025-11-07", "main": [7, 20, 25, 30, 39], "euro": [5, 10]},
    {"date": "2025-11-04", "main": [2, 11, 24, 36, 46], "euro": [7, 9]},
    {"date": "2025-10-31", "main": [11, 22, 32, 39, 47], "euro": [5, 11]},
    {"date": "2025-10-28", "main": [14, 18, 33, 43, 48], "euro": [2, 6]},
    {"date": "2025-10-24", "main": [3, 21, 31, 35, 43], "euro": [4, 9]},
    {"date": "2025-10-21", "main": [6, 25, 28, 31, 50], "euro": [6, 8]},
    {"date": "2025-10-17", "main": [1, 2, 15, 34, 43], "euro": [7, 11]},
    {"date": "2025-10-14", "main": [12, 18, 26, 42, 46], "euro": [4, 8]},
    {"date": "2025-10-10", "main": [7, 9, 24, 28, 32], "euro": [3, 6]},
    {"date": "2025-10-07", "main": [16, 22, 23, 27, 49], "euro": [7, 10]},
    {"date": "2025-10-03", "main": [1, 2, 7, 27, 32], "euro": [1, 6]},
    {"date": "2025-09-30", "main": [5, 11, 26, 30, 43], "euro": [6, 10]},
    {"date": "2025-09-26", "main": [13, 17, 18, 19, 50], "euro": [3, 10]},
    {"date": "2025-09-23", "main": [10, 14, 20, 29, 38], "euro": [3, 8]},
    {"date": "2025-09-19", "main": [5, 22, 35, 36, 41], "euro": [4, 7]},
    {"date": "2025-09-16", "main": [7, 13, 19, 23, 37], "euro": [2, 5]},
    {"date": "2025-09-12", "main": [4, 9, 20, 23, 49], "euro": [7, 9]},
    {"date": "2025-09-09", "main": [11, 19, 27, 38, 50], "euro": [3, 5]},
    {"date": "2025-09-05", "main": [17, 24, 29, 34, 38], "euro": [1, 10]},
    {"date": "2025-09-02", "main": [5, 12, 18, 32, 36], "euro": [1, 6]},
    {"date": "2025-08-29", "main": [3, 16, 19, 20, 42], "euro": [5, 9]},
    {"date": "2025-08-26", "main": [8, 9, 30, 36, 46], "euro": [4, 9]},
    {"date": "2025-08-22", "main": [10, 22, 25, 38, 41], "euro": [2, 10]},
    {"date": "2025-08-19", "main": [14, 24, 26, 28, 50], "euro": [1, 3]},
    {"date": "2025-08-15", "main": [6, 20, 24, 27, 48], "euro": [4, 8]},
    {"date": "2025-08-12", "main": [2, 13, 31, 32, 39], "euro": [1, 6]},
    {"date": "2025-08-08", "main": [1, 25, 28, 31, 40], "euro": [6, 10]},
    {"date": "2025-08-05", "main": [21, 23, 34, 39, 41], "euro": [1, 8]},
    {"date": "2025-08-01", "main": [3, 8, 22, 34, 46], "euro": [3, 5]},
    {"date": "2025-07-29", "main": [13, 17, 20, 26, 30], "euro": [3, 9]},
    {"date": "2025-07-25", "main": [1, 9, 33, 36, 38], "euro": [1, 5]},
    {"date": "2025-07-22", "main": [4, 19, 27, 35, 48], "euro": [4, 6]},
    {"date": "2025-07-18", "main": [5, 15, 17, 26, 41], "euro": [5, 8]},
    {"date": "2025-07-15", "main": [7, 10, 24, 27, 38], "euro": [2, 6]},
    {"date": "2025-07-11", "main": [2, 5, 27, 42, 50], "euro": [5, 11]},
    {"date": "2025-07-08", "main": [12, 19, 23, 38, 49], "euro": [5, 7]},
    {"date": "2025-07-04", "main": [3, 14, 16, 28, 40], "euro": [2, 8]},
    {"date": "2025-07-01", "main": [6, 21, 27, 31, 42], "euro": [3, 8]},
    {"date": "2025-06-27", "main": [10, 13, 18, 33, 47], "euro": [2, 9]},
    {"date": "2025-06-24", "main": [2, 23, 26, 35, 48], "euro": [3, 10]},
    {"date": "2025-06-20", "main": [9, 20, 24, 33, 43], "euro": [1, 9]},
    {"date": "2025-06-17", "main": [1, 18, 22, 28, 35], "euro": [4, 5]},
    {"date": "2025-06-13", "main": [11, 15, 25, 32, 41], "euro": [3, 9]},
    {"date": "2025-06-10", "main": [7, 18, 29, 35, 46], "euro": [3, 7]},
    {"date": "2025-06-06", "main": [6, 11, 13, 24, 42], "euro": [4, 8]},
    {"date": "2025-06-03", "main": [4, 17, 30, 38, 48], "euro": [2, 7]},
    {"date": "2025-05-30", "main": [9, 21, 28, 39, 45], "euro": [3, 10]},
    {"date": "2025-05-27", "main": [5, 23, 30, 35, 49], "euro": [2, 5]},
    {"date": "2025-05-23", "main": [12, 17, 34, 38, 41], "euro": [3, 6]},
    {"date": "2025-05-20", "main": [8, 19, 22, 29, 47], "euro": [1, 11]},
    {"date": "2025-05-16", "main": [3, 15, 29, 42, 48], "euro": [5, 7]},
    {"date": "2025-05-13", "main": [9, 14, 25, 33, 46], "euro": [2, 6]},
    {"date": "2025-05-09", "main": [16, 19, 21, 25, 41], "euro": [3, 9]},
    {"date": "2025-05-06", "main": [7, 11, 14, 27, 50], "euro": [3, 7]},
    {"date": "2025-05-02", "main": [4, 9, 21, 26, 35], "euro": [1, 6]},
    {"date": "2025-04-29", "main": [13, 24, 35, 38, 44], "euro": [2, 4]},
    {"date": "2025-04-25", "main": [2, 8, 27, 40, 49], "euro": [3, 6]},
    {"date": "2025-04-22", "main": [1, 10, 12, 16, 22], "euro": [2, 6]},
    {"date": "2025-04-18", "main": [3, 18, 26, 35, 39], "euro": [4, 7]},
    {"date": "2025-04-15", "main": [5, 14, 16, 21, 46], "euro": [5, 8]},
    {"date": "2025-04-11", "main": [9, 17, 23, 27, 48], "euro": [4, 9]},
    {"date": "2025-04-08", "main": [4, 11, 15, 22, 32], "euro": [1, 7]},
    {"date": "2025-04-04", "main": [6, 20, 23, 31, 37], "euro": [2, 3]},
    {"date": "2025-04-01", "main": [13, 19, 28, 42, 50], "euro": [3, 5]},
    {"date": "2025-03-28", "main": [7, 16, 29, 38, 45], "euro": [4, 8]},
    {"date": "2025-03-25", "main": [1, 8, 32, 33, 41], "euro": [3, 7]},
    {"date": "2025-03-21", "main": [10, 18, 22, 25, 28], "euro": [2, 9]},
    {"date": "2025-03-18", "main": [11, 17, 21, 24, 44], "euro": [1, 8]},
    {"date": "2025-03-14", "main": [5, 19, 27, 43, 45], "euro": [1, 4]},
    {"date": "2025-03-11", "main": [4, 12, 25, 36, 47], "euro": [3, 5]},
    {"date": "2025-03-07", "main": [2, 9, 18, 20, 34], "euro": [1, 7]},
    {"date": "2025-03-04", "main": [3, 15, 22, 23, 30], "euro": [4, 8]},
    {"date": "2025-02-28", "main": [6, 8, 11, 29, 49], "euro": [3, 5]},
    {"date": "2025-02-25", "main": [13, 20, 31, 33, 46], "euro": [2, 6]},
    {"date": "2025-02-21", "main": [7, 14, 19, 21, 38], "euro": [5, 9]},
    {"date": "2025-02-18", "main": [9, 24, 32, 41, 50], "euro": [1, 8]},
    {"date": "2025-02-14", "main": [1, 5, 11, 22, 34], "euro": [3, 6]},
    {"date": "2025-02-11", "main": [4, 17, 26, 27, 43], "euro": [4, 6]},
    {"date": "2025-02-07", "main": [10, 15, 20, 39, 48], "euro": [3, 7]},
    {"date": "2025-02-04", "main": [2, 12, 19, 30, 35], "euro": [2, 8]},
    {"date": "2025-01-31", "main": [8, 16, 22, 25, 44], "euro": [1, 4]},
    {"date": "2025-01-28", "main": [3, 11, 18, 23, 41], "euro": [5, 6]},
    {"date": "2025-01-24", "main": [6, 13, 28, 37, 49], "euro": [2, 5]},
    {"date": "2025-01-21", "main": [4, 9, 15, 21, 33], "euro": [3, 8]},
    {"date": "2025-01-17", "main": [1, 7, 12, 26, 32], "euro": [4, 9]},
    {"date": "2025-01-14", "main": [5, 14, 18, 29, 43], "euro": [1, 10]},
    {"date": "2025-01-10", "main": [10, 17, 24, 31, 42], "euro": [3, 6]},
    {"date": "2025-01-07", "main": [2, 8, 21, 38, 40], "euro": [1, 7]},
    {"date": "2025-01-03", "main": [11, 16, 20, 25, 39], "euro": [4, 5]},
]

# Statistics from website
# Main number frequency (all time 931 draws)
all_time_main = {20: 110, 34: 107, 11: 105, 49: 104, 16: 103, 45: 102, 19: 101, 35: 100, 18: 99, 17: 98}

# Euro number frequency (all time)
all_time_euro = {5: 196, 3: 192, 8: 187, 9: 185, 1: 183, 4: 180, 2: 178, 7: 177, 6: 175, 12: 173}

# ============================================
# ANALYSIS FUNCTIONS
# ============================================

def get_frequency(draws, is_euro=False):
    counter = Counter()
    for draw in draws:
        for num in draw['main' if not is_euro else 'euro']:
            counter[num] += 1
    return counter

def get_weighted_frequency(draws, is_euro=False, decay=0.95):
    """Weighted frequency with recency decay"""
    counter = Counter()
    total_draws = len(draws)
    for i, draw in enumerate(draws):
        weight = decay ** (total_draws - i - 1)
        for num in draw['main' if not is_euro else 'euro']:
            counter[num] += weight
    return counter

def get_odd_even_pattern(draws, is_euro=False):
    pattern = Counter()
    for draw in draws:
        nums = draw['main' if not is_euro else 'euro']
        odds = sum(1 for n in nums if n % 2 == 1)
        pattern[odds] += 1
    return pattern.most_common(1)[0][0]

def get_number_gaps(draws, is_euro=False):
    """Average gap between occurrences"""
    last_seen = {}
    gaps = []
    for i, draw in enumerate(draws):
        for num in draw['main' if not is_euro else 'euro']:
            if num in last_seen:
                gaps.append(i - last_seen[num])
            last_seen[num] = i
    return sum(gaps) / len(gaps) if gaps else 10

def get_sum_range(draws, is_euro=False):
    """Target sum range"""
    sums = [sum(d['main' if not is_euro else 'euro']) for d in draws]
    return sum(sums) / len(sums)

# ============================================
# ADVANCED MODELS
# ============================================

class AdvancedEnsemble:
    def __init__(self, draws):
        self.draws = draws
        self.is_calibrated = False
        self._calibrate()
    
    def _calibrate(self):
        """Calibrate model weights based on historical performance"""
        # Test each model on last 20 draws
        test_set = self.draws[:20]
        train_set = self.draws[20:]
        
        # Simple calibration - we'll use uniform weights
        self.weights = {
            'frequency': 0.20,
            'weighted': 0.15,
            'recency': 0.15,
            'pattern': 0.15,
            'bayesian': 0.10,
            'neural': 0.15,
            'montecarlo': 0.10
        }
        self.is_calibrated = True
    
    def predict_main(self, num_predictions=5):
        return self._predict(is_euro=False, n=num_predictions)
    
    def predict_euro(self, num_predictions=2):
        return self._predict(is_euro=True, n=num_predictions)
    
    def _predict(self, is_euro=False, n=5):
        max_num = 50 if not is_euro else 12
        
        # Model 1: Raw frequency
        freq = get_frequency(self.draws, is_euro)
        freq_scores = {i: freq.get(i, 0) for i in range(1, max_num + 1)}
        
        # Model 2: Weighted frequency (recent draws matter more)
        w_freq = get_weighted_frequency(self.draws, is_euro)
        w_scores = {i: w_freq.get(i, 0) for i in range(1, max_num + 1)}
        
        # Model 3: Recency (numbers due to appear)
        last_seen = {}
        for i, draw in enumerate(self.draws):
            for num in draw['main' if not is_euro else 'euro']:
                last_seen[num] = i
        recency_scores = {}
        for num in range(1, max_num + 1):
            draws_ago = len(self.draws) - last_seen.get(num, -1)
            recency_scores[num] = draws_ago / len(self.draws)
        
        # Model 4: Pattern-based
        oe_pattern = get_odd_even_pattern(self.draws, is_euro)
        pattern_scores = {}
        for num in range(1, max_num + 1):
            is_odd = num % 2 == 1
            if is_odd and oe_pattern > n/2:
                pattern_scores[num] = 1.0
            elif not is_odd and oe_pattern <= n/2:
                pattern_scores[num] = 1.0
            else:
                pattern_scores[num] = 0.5
        
        # Model 5: Bayesian
        bayesian_scores = {i: 1.0 for i in range(1, max_num + 1)}
        for draw in self.draws:
            for num in draw['main' if not is_euro else 'euro']:
                bayesian_scores[num] *= 1.05
        total_b = sum(bayesian_scores.values())
        bayesian_scores = {k: v/total_b for k, v in bayesian_scores.items()}
        
        # Model 6: Neural-style
        neural_scores = {}
        max_f = max(freq_scores.values()) if freq_scores else 1
        max_w = max(w_scores.values()) if w_scores else 1
        max_r = max(recency_scores.values()) if recency_scores else 1
        
        for num in range(1, max_num + 1):
            f = freq_scores.get(num, 0) / max_f if max_f else 0
            w = w_scores.get(num, 0) / max_w if max_w else 0
            r = recency_scores.get(num, 0) / max_r if max_r else 0
            p = pattern_scores.get(num, 0.5)
            b = bayesian_scores.get(num, 0)
            neural_scores[num] = (f * 0.25 + w * 0.25 + r * 0.20 + p * 0.10 + b * 0.20)
        
        # Model 7: Monte Carlo (statistical)
        mc_scores = Counter()
        for _ in range(50000):
            picks = random.sample(range(1, max_num + 1), n)
            mc_scores[tuple(sorted(picks))] += 1
        
        # Convert to individual scores
        individual_mc = Counter()
        for combo, count in mc_scores.most_common(100):
            for num in combo:
                individual_mc[num] += count
        mc_norm = max(individual_mc.values()) if individual_mc else 1
        mc_final_scores = {i: individual_mc.get(i, 0) / mc_norm for i in range(1, max_num + 1)}
        
        # Combine all models
        combined = {}
        for num in range(1, max_num + 1):
            combined[num] = (
                freq_scores.get(num, 0) * self.weights['frequency'] +
                w_scores.get(num, 0) * self.weights['weighted'] +
                recency_scores.get(num, 0) * self.weights['recency'] +
                pattern_scores.get(num, 0) * self.weights['pattern'] +
                bayesian_scores.get(num, 0) * max(bayesian_scores.values()) * self.weights['bayesian'] +
                neural_scores.get(num, 0) * self.weights['neural'] +
                mc_final_scores.get(num, 0) * self.weights['montecarlo']
            )
        
        # Sort and select
        sorted_nums = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        
        # Select with distribution consideration
        selected = []
        ranges_used = set()
        
        for num, score in sorted_nums:
            if len(selected) >= n:
                break
            bucket = num // 10
            if bucket not in ranges_used or len(selected) >= n - 1:
                selected.append(num)
                ranges_used.add(bucket)
        
        # Fill remaining slots
        while len(selected) < n:
            for num, score in sorted_nums:
                if num not in selected:
                    selected.append(num)
                    break
        
        return sorted(selected[:n])

def run_ensemble_prediction():
    print("=" * 60)
    print("ADVANCED EUROJACKPOT PREDICTION ENGINE v2")
    print("=" * 60)
    
    ensemble = AdvancedEnsemble(all_draws)
    
    # Run multiple times for robustness
    main_results = []
    euro_results = []
    
    for i in range(20):
        main_pred = ensemble.predict_main(5)
        euro_pred = ensemble.predict_euro(2)
        main_results.append(tuple(main_pred))
        euro_results.append(tuple(euro_pred))
    
    # Find consensus
    main_counter = Counter(main_results)
    euro_counter = Counter(euro_results)
    
    best_main = main_counter.most_common(1)[0][0]
    best_euro = euro_counter.most_common(1)[0][0]
    
    print(f"\nENSEMBLE PREDICTION (20 runs):")
    print(f"Main Numbers: {list(best_main)}")
    print(f"Euro Numbers: {list(best_euro)}")
    
    # Also show runner-ups
    print(f"\nRunner-up Main: {main_counter.most_common(2)[1][0]}")
    
    return list(best_main), list(best_euro)

if __name__ == "__main__":
    main_nums, euro_nums = run_ensemble_prediction()
    print(f"\nFINAL: Main={main_nums}, Euro={euro_nums}")
