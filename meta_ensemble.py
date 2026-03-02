"""
META-ENSEMBLE: Combining all prediction models
"""

import random
from collections import Counter

random.seed(20260224)

# Historical data
draws = [
    {"main": [11, 17, 23, 36, 40], "euro": [5, 6]},
    {"main": [8, 23, 39, 40, 44], "euro": [6, 7]},
    {"main": [1, 21, 44, 45, 46], "euro": [2, 7]},
    {"main": [12, 19, 34, 39, 47], "euro": [4, 5]},
    {"main": [8, 14, 38, 41, 48], "euro": [1, 11]},
    {"main": [3, 20, 27, 37, 44], "euro": [1, 2]},
    {"main": [8, 13, 15, 17, 37], "euro": [3, 7]},
    {"main": [13, 18, 19, 29, 32], "euro": [8, 9]},
    {"main": [18, 36, 39, 45, 50], "euro": [6, 9]},
    {"main": [16, 26, 32, 37, 45], "euro": [2, 3]},
    {"main": [9, 13, 22, 24, 49], "euro": [3, 10]},
    {"main": [2, 6, 22, 35, 43], "euro": [2, 12]},
    {"main": [1, 17, 19, 27, 41], "euro": [3, 7]},
    {"main": [11, 15, 30, 38, 41], "euro": [9, 10]},
    {"main": [10, 18, 21, 35, 44], "euro": [1, 6]},
    {"main": [21, 26, 34, 37, 38], "euro": [1, 3]},
    {"main": [15, 29, 35, 42, 49], "euro": [4, 9]},
    {"main": [18, 36, 39, 45, 50], "euro": [6, 9]},
    {"main": [9, 22, 27, 40, 41], "euro": [7, 9]},
    {"main": [6, 20, 31, 32, 44], "euro": [6, 7]},
    {"main": [19, 24, 29, 35, 42], "euro": [3, 8]},
    {"main": [7, 17, 25, 41, 49], "euro": [4, 7]},
    {"main": [4, 6, 18, 24, 50], "euro": [4, 10]},
    {"main": [1, 13, 21, 27, 46], "euro": [5, 9]},
    {"main": [5, 11, 14, 35, 48], "euro": [6, 9]},
    {"main": [6, 17, 21, 29, 40], "euro": [3, 11]},
    {"main": [15, 19, 29, 41, 50], "euro": [5, 8]},
    {"main": [4, 16, 28, 35, 49], "euro": [5, 10]},
    {"main": [5, 18, 19, 33, 42], "euro": [5, 9]},
    {"main": [9, 10, 23, 36, 48], "euro": [4, 9]},
]

# All-time frequencies (from website)
main_alltime = {20: 110, 34: 107, 11: 105, 49: 104, 16: 103, 45: 102, 19: 101, 35: 100, 18: 99, 17: 98}
euro_alltime = {5: 196, 3: 192, 8: 187, 9: 185, 1: 183, 4: 180, 2: 178, 7: 177, 6: 175, 12: 173}

# Analyze recent draws
def get_freq(draws, is_euro=False):
    c = Counter()
    for d in draws:
        for n in d['main' if not is_euro else 'euro']:
            c[n] += 1
    return c

def get_recency(draws, is_euro=False):
    last = {}
    for i, d in enumerate(draws):
        for n in d['main' if not is_euro else 'euro']:
            last[n] = i
    scores = {}
    for n in range(1, 51 if not is_euro else 13):
        scores[n] = len(draws) - last.get(n, -1)
    return scores

# Score each number using multiple factors
def score_numbers(draws, is_euro=False, alltime_freq=None):
    max_num = 50 if not is_euro else 12
    
    # Factor 1: Recent frequency
    recent = get_freq(draws[:15], is_euro)
    max_recent = max(recent.values()) if recent else 1
    
    # Factor 2: All-time frequency
    at = alltime_freq or {}
    max_at = max(at.values()) if at else 1
    
    # Factor 3: Recency (numbers due)
    rec = get_recency(draws, is_euro)
    max_rec = max(rec.values()) if rec else 1
    
    # Factor 4: Odd/even preference
    oe_prefs = []
    for d in draws:
        nums = d['main' if not is_euro else 'euro']
        oe_prefs.append(sum(1 for n in nums if n % 2 == 1))
    avg_odd = sum(oe_prefs) / len(oe_prefs)
    
    scores = {}
    for n in range(1, max_num + 1):
        # Recent frequency weight
        rf = recent.get(n, 0) / max_recent * 0.35
        
        # All-time frequency weight
        af = at.get(n, 0) / max_at * 0.25 if at else 0
        
        # Recency weight
        rc = rec.get(n, 0) / max_rec * 0.25
        
        # Odd/even weight
        is_odd = n % 2 == 1
        oe = 1.0 if (is_odd and avg_odd > 2.5) or (not is_odd and avg_odd < 2.5) else 0.5
        oe_weight = oe * 0.15
        
        scores[n] = rf + af + rc + oe_weight
    
    return scores

# Get scores
main_scores = score_numbers(draws, False, main_alltime)
euro_scores = score_numbers(draws, True, euro_alltime)

# Add some Monte Carlo variation
for n in main_scores:
    main_scores[n] += random.random() * 0.1
for n in euro_scores:
    euro_scores[n] += random.random() * 0.1

# Sort and select with distribution
def select_with_distribution(scores, n_select):
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    selected = []
    used = set()
    for num, score in sorted_nums:
        bucket = num // 10
        if bucket not in used or len(selected) >= n_select - 1:
            selected.append(num)
            used.add(bucket)
        if len(selected) >= n_select:
            break
    # Fill
    while len(selected) < n_select:
        for num, score in sorted_nums:
            if num not in selected:
                selected.append(num)
                break
    return sorted(selected[:n_select])

main_final = select_with_distribution(main_scores, 5)
euro_final = select_with_distribution(euro_scores, 2)

print("=" * 60)
print("META-ENSEMBLE FINAL PREDICTION")
print("=" * 60)
print(f"\nMAIN NUMBERS: {main_final}")
print(f"EURO NUMBERS: {euro_final}")

# Show top candidates
print("\nTop 10 Main Candidates:")
for n, s in sorted(main_scores.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {n}: {s:.3f}")

print("\nTop Euro Candidates:")
for n, s in sorted(euro_scores.items(), key=lambda x: x[1], reverse=True)[:6]:
    print(f"  {n}: {s:.3f}")
