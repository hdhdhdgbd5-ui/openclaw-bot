"""
FINAL CONSENSUS PREDICTION
==========================
Aggregates all models for final prediction
"""

import random
from collections import Counter

# Run all models multiple times and aggregate

def model1(draws, is_euro=False):
    """Frequency model"""
    c = Counter()
    for d in draws:
        for n in d['main' if not is_euro else 'euro']:
            c[n] += 1
    max_n = 50 if not is_euro else 12
    return sorted(c.keys(), key=lambda x: c[x], reverse=True)[:5 if not is_euro else 2]

def model2(draws, is_euro=False):
    """Recency model"""
    last = {}
    for i, d in enumerate(draws):
        for n in d['main' if not is_euro else 'euro']:
            last[n] = i
    max_n = 50 if not is_euro else 12
    scores = [(n, len(draws) - last.get(n, -1)) for n in range(1, max_n + 1)]
    return [n for n, s in sorted(scores, key=lambda x: x[1], reverse=True)[:5 if not is_euro else 2]]

def model3(draws, is_euro=False):
    """Weighted frequency (recent draws weighted more)"""
    c = Counter()
    for i, d in enumerate(draws):
        w = 1 + (len(draws) - i) * 0.1
        for n in d['main' if not is_euro else 'euro']:
            c[n] += w
    max_n = 50 if not is_euro else 12
    return sorted(c.keys(), key=lambda x: c[x], reverse=True)[:5 if not is_euro else 2]

def model4(draws, is_euro=False):
    """Pattern model (odd/even)"""
    oe = []
    for d in draws:
        nums = d['main' if not is_euro else 'euro']
        oe.append(sum(1 for n in nums if n % 2 == 1))
    avg_odd = sum(oe) / len(oe)
    
    max_n = 50 if not is_euro else 12
    c = Counter()
    for d in draws:
        for n in d['main' if not is_euro else 'euro']:
            c[n] += 1
    
    scored = []
    for n in range(1, max_n + 1):
        is_odd = n % 2 == 1
        oe_bonus = 1.3 if (is_odd and avg_odd > 2.5) or (not is_odd and avg_odd < 2.5) else 1.0
        scored.append((n, c.get(n, 0) * oe_bonus))
    
    return [n for n, s in sorted(scored, key=lambda x: x[1], reverse=True)[:5 if not is_euro else 2]]

def model5(draws, is_euro=False):
    """All-time hot numbers"""
    main_hot = [20, 34, 11, 49, 16, 45, 19, 35, 18, 17]
    euro_hot = [5, 3, 8, 9, 1, 4, 2, 7, 6, 12]
    hot = main_hot if not is_euro else euro_hot
    return hot[:5 if not is_euro else 2]

def model6(draws, is_euro=False):
    """Monte Carlo simulation"""
    max_n = 50 if not is_euro else 12
    n_select = 5 if not is_euro else 2
    results = Counter()
    for _ in range(10000):
        picks = tuple(sorted(random.sample(range(1, max_n + 1), n_select)))
        results[picks] += 1
    best = results.most_common(1)[0][0]
    return list(best)

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

models = [model1, model2, model3, model4, model5, model6]

# Run all models multiple times
main_votes = Counter()
euro_votes = Counter()

for _ in range(30):
    for m in models:
        main_pred = tuple(m(draws, False))
        euro_pred = tuple(m(draws, True))
        main_votes[main_pred] += 1
        euro_votes[euro_pred] += 1

print("=" * 60)
print("CONSENSUS PREDICTION")
print("=" * 60)

print("\nTop Main Combinations:")
for combo, votes in main_votes.most_common(5):
    print(f"  {list(combo)}: {votes}")

print("\nTop Euro Combinations:")
for combo, votes in euro_votes.most_common(5):
    print(f"  {list(combo)}: {votes}")

best_main = main_votes.most_common(1)[0][0]
best_euro = euro_votes.most_common(1)[0][0]

print(f"\n{'='*60}")
print(f"FINAL PREDICTION:")
print(f"MAIN NUMBERS: {list(best_main)}")
print(f"EURO NUMBERS: {list(best_euro)}")
print(f"{'='*60}")

# Also show individual number frequency
print("\nIndividual Main Number Frequency in Top Predictions:")
individual_main = Counter()
for combo, votes in main_votes.items():
    for num in combo:
        individual_main[num] += votes
for num, count in individual_main.most_common(10):
    print(f"  {num}: {count}")

print("\nIndividual Euro Number Frequency in Top Predictions:")
individual_euro = Counter()
for combo, votes in euro_votes.items():
    for num in combo:
        individual_euro[num] += votes
for num, count in individual_euro.most_common(5):
    print(f"  {num}: {count}")
