"""
Lottery Number Generator
Generate lottery numbers using various strategies
"""
import random
import json
from typing import Dict, List, Optional, Tuple
from collections import Counter

class LotteryGenerator:
    """Generate lottery numbers using various strategies"""
    
    def __init__(self):
        self.lotteries = {
            "eurojackpot": {"main": (5, 50), "extra": (2, 10)},
            "euromillions": {"main": (5, 50), "extra": (2, 12)},
            "powerball": {"main": (5, 69), "extra": (1, 26)},
            "megamillions": {"main": (5, 70), "extra": (1, 25)},
        }
        
    def generate_random(self, lottery: str = "eurojackpot", count: Optional[int] = None, extra_range: Optional[Tuple[int, int]] = None) -> Dict:
        """Generate random lottery numbers"""
        if lottery not in self.lotteries:
            lottery = "eurojackpot"
            
        config = self.lotteries[lottery]
        main_count, main_max = config["main"]
        
        if count:
            main_count = count
            
        # Generate main numbers
        main_numbers = sorted(random.sample(range(1, main_max + 1), main_count))
        
        result = {
            "lottery": lottery,
            "main": main_numbers,
            "strategy": "random"
        }
        
        # Generate extra numbers if applicable
        if extra_range or (config["extra"][0] > 0):
            extra_count, extra_max = config["extra"]
            if extra_range:
                extra_count, extra_max = extra_range[0], extra_range[1]
            extra_numbers = sorted(random.sample(range(1, extra_max + 1), extra_count))
            result["extra"] = extra_numbers
            
        return result
        
    def generate_balanced(self, lottery: str = "eurojackpot") -> Dict:
        """Generate balanced numbers (mix of high/low and odd/even)"""
        if lottery not in self.lotteries:
            lottery = "eurojackpot"
            
        config = self.lotteries[lottery]
        main_count, main_max = config["main"]
        
        # Split range into halves
        low_half = list(range(1, main_max // 2 + 1))
        high_half = list(range(main_max // 2 + 1, main_max + 1))
        
        main_numbers = []
        
        # Ensure mix of low/high
        main_numbers.extend(random.sample(low_half, main_count // 2))
        main_numbers.extend(random.sample(high_half, main_count - main_count // 2))
        
        # Ensure mix of odd/even
        while len(main_numbers) < main_count:
            num = random.randint(1, main_max)
            if num not in main_numbers:
                if (num % 2 == 0 and sum(n % 2 == 0 for n in main_numbers) < main_count // 2) or \
                   (num % 2 != 0 and sum(n % 2 != 0 for n in main_numbers) < main_count // 2):
                    main_numbers.append(num)
                    
        main_numbers = sorted(main_numbers)[:main_count]
        
        result = {
            "lottery": lottery,
            "main": main_numbers,
            "strategy": "balanced"
        }
        
        if config["extra"][0] > 0:
            extra_count, extra_max = config["extra"]
            extra_numbers = sorted(random.sample(range(1, extra_max + 1), extra_count))
            result["extra"] = extra_numbers
            
        return result
        
    def generate_with_strategy(self, lottery: str = "eurojackpot", strategy: str = "random") -> Dict:
        """Generate numbers with specific strategy"""
        if strategy == "balanced":
            return self.generate_balanced(lottery)
        else:
            return self.generate_random(lottery)
            
    def analyze_history(self, numbers: List[int]) -> Dict:
        """Analyze historical numbers to find hot/cold numbers"""
        counter = Counter(numbers)
        total = len(numbers)
        
        # Find hot numbers (appeared frequently)
        hot_numbers = [num for num, count in counter.most_common(10)]
        
        # Find cold numbers (appeared rarely)
        all_numbers = list(range(1, 51)) # Assuming 1-50 range
        cold_numbers = [num for num in all_numbers if num not in counter]
        
        return {
            "frequency": dict(counter),
            "hot_numbers": hot_numbers,
            "cold_numbers": cold_numbers[:10],
            "total_draws": total
        }
        
# Example usage
if __name__ == "__main__":
    gen = LotteryGenerator()
    
    # Random
    print("Random:", gen.generate_random())
    
    # Balanced
    print("Balanced:", gen.generate_balanced())
    
    # Analysis
    history = [1, 2, 3, 4, 5, 1, 2, 3, 1, 2, 10, 15, 20, 25, 30]
    print("Analysis:", gen.analyze_history(history))
