# Lottery Number Generator Skill

Generate lottery numbers (EuroJackpot, Powerball, etc.) using various strategies.

## Features

- **Random Generation**: Pure random number generation
- **Statistical Analysis**: Use historical data to pick numbers
- **Pattern Detection**: Detect hot/cold numbers
- **AI Prediction**: Use AI to predict numbers (if model available)
- **Multiple Lotteries**: Support for various lottery formats

## Usage

### Python API

```python
from lottery_number_generator import LotteryGenerator

# Initialize
generator = LotteryGenerator()

# Generate random numbers
numbers = generator.generate_random(
    lottery="eurojackpot",
    count=5,
    extra_range=(1, 10)
)
# Result: [3, 14, 22, 35, 41], Extra: [7]

# Generate with strategy
numbers = generator.generate_with_strategy(
    lottery="eurojackpot",
    strategy="balanced"
)

# Analyze historical data
analysis = generator.analyze_history([1, 2, 3, 4, 5, 6])
# Returns: hot_numbers, cold_numbers, frequency
```

## Supported Lotteries

- EuroJackpot (5/50 + 2/10)
- EuroMillions (5/50 + 2/12)
- Powerball (5/69 + 1/26)
- MegaMillions (5/70 + 1/25)
- Custom

## Strategies

- `random`: Pure random
- `balanced`: Mix of high/low and odd/even
- `hot`: Frequently drawn numbers
- `cold`: Least frequently drawn numbers
- `AI`: AI prediction (if available)

## Installation

```bash
pip install random
```

## License

MIT
