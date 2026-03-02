"""
FINAL EUROJACKPOT PREDICTION - ROBUST VERSION
==============================================
"""

import random
from collections import Counter

# Set seed for reproducibility
random.seed(20260224)

all_draws = [
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

def analyze(draws, is_euro=False):
    counter = Counter()
    for d in draws:
        for n in d['main' if not is_euro else 'euro']:
            counter[n] += 1
    return counter

# Run 50 simulations
main_votes = Counter()
euro_votes = Counter()

for _ in range(50):
    # Frequency based scoring
    main_freq = analyze(all_draws, False)
    euro_freq = analyze(all_draws, True)
    
    # Weighted by recency
    weights = {}
    for i, d in enumerate(all_draws):
        w = 1 + (len(all_draws) - i) * 0.1
        for n in d['main']:
            weights[(n, False)] = weights.get((n, False), 0) + w
        for n in d['euro']:
            weights[(n, True)] = weights.get((n, True), 0) + w
    
    # Score each number
    main_scores = {}
    euro_scores = {}
    for n in range(1, 51):
        main_scores[n] = main_freq.get(n, 0) * 1.0 + weights.get((n, False), 0) * 0.5
    for n in range(1, 13):
        euro_scores[n] = euro_freq.get(n, 0) * 1.0 + weights.get((n, True), 0) * 0.5
    
    # Add some randomness (Monte Carlo element)
    for n in main_scores:
        main_scores[n] += random.random() * 5
    for n in euro_scores:
        euro_scores[n] += random.random() * 3
    
    # Select top
    main_sorted = sorted(main_scores.items(), key=lambda x: x[1], reverse=True)
    euro_sorted = sorted(euro_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Pick with some distribution
    selected_main = []
    used_ranges = set()
    for n, s in main_sorted:
        bucket = n // 10
        if bucket not in used_ranges or len(selected_main) >= 4:
            selected_main.append(n)
            used_ranges.add(bucket)
        if len(selected_main) >= 5:
            break
    while len(selected_main) < 5:
        for n, s in main_sorted:
            if n not in selected_main:
                selected_main.append(n)
                break
    
    selected_euro = []
    for n, s in euro_sorted:
        if n not in selected_euro:
            selected_euro.append(n)
        if len(selected_euro) >= 2:
            break
    
    main_votes[tuple(sorted(selected_main))] += 1
    euro_votes[tuple(sorted(selected_euro))] += 1

print("MAIN NUMBERS voting:")
for combo, votes in main_votes.most_common(5):
    print(f"  {combo}: {votes} votes")

print("\nEURO NUMBERS voting:")
for combo, votes in euro_votes.most_common(5):
    print(f"  {combo}: {votes} votes")

print("\n" + "="*50)
print("FINAL PREDICTION:")
best_main = main_votes.most_common(1)[0][0]
best_euro = euro_votes.most_common(1)[0][0]
print(f"MAIN: {list(best_main)}")
print(f"EURO: {list(best_euro)}")
