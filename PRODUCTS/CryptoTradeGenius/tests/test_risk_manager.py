"""
Tests for Risk Management System
"""

import pytest
from src.risk.risk_manager import RiskManager, PositionRisk


@pytest.fixture
def risk_manager():
    return RiskManager()


def test_position_risk_calculation():
    """Test position risk calculations"""
    position = PositionRisk(
        symbol="BTC/USDT",
        entry_price=50000,
        current_price=51000,
        quantity=0.1,
        stop_loss=49000,
        take_profit=55000
    )
    
    assert position.position_value == 5100
    assert position.unrealized_pnl == 100
    assert position.unrealized_pnl_percent == 2.0
    assert position.risk_amount == 100  # (50000 - 49000) * 0.1


def test_can_open_position_basic(risk_manager):
    """Test basic position opening checks"""
    # Should allow first position
    allowed, reason = risk_manager.can_open_position("BTC/USDT", 1000, 10000)
    assert allowed is True
    assert reason == "OK"


def test_position_sizing(risk_manager):
    """Test position size calculation"""
    quantity, risk_percent = risk_manager.calculate_position_size(
        entry_price=50000,
        stop_loss=49000,
        portfolio_value=10000
    )
    
    # With 2% max risk per trade
    # Risk amount = $200
    # Price risk = $1000 per BTC
    # Quantity should be around 0.2 BTC
    assert quantity > 0
    assert risk_percent <= 2.5  # Allow small rounding


def test_stop_loss_calculation(risk_manager):
    """Test stop loss calculation"""
    # Long position
    stop = risk_manager.calculate_stop_loss(
        entry_price=50000,
        side="buy",
        method="percent"
    )
    # Default 3% stop
    assert stop == 50000 * 0.97
    
    # Short position
    stop = risk_manager.calculate_stop_loss(
        entry_price=50000,
        side="sell",
        method="percent"
    )
    assert stop == 50000 * 1.03


def test_take_profit_calculation(risk_manager):
    """Test take profit calculation"""
    tp = risk_manager.calculate_take_profit(
        entry_price=50000,
        stop_loss=48500,
        side="buy",
        risk_reward=2.0
    )
    
    # Stop distance = $1500
    # 2x risk reward = $3000 profit
    # Take profit = $53000
    assert tp == 53000


def test_daily_loss_limit(risk_manager):
    """Test daily loss limit enforcement"""
    # Simulate daily loss at limit
    risk_manager.daily_stats["starting_equity"] = 10000
    risk_manager.daily_stats["total_pnl"] = -500  # 5% loss
    
    allowed, reason = risk_manager.can_open_position("ETH/USDT", 1000, 10000)
    # Should be blocked due to daily loss limit
    assert allowed is False
    assert "Daily loss limit" in reason


def test_max_positions_limit(risk_manager):
    """Test maximum positions limit"""
    # Fill up positions
    for i in range(10):
        risk_manager.position_risks[f"COIN{i}/USDT"] = PositionRisk(
            symbol=f"COIN{i}/USDT",
            entry_price=100,
            current_price=100,
            quantity=1,
            stop_loss=95,
            take_profit=110
        )
    
    allowed, reason = risk_manager.can_open_position("NEW/USDT", 1000, 10000)
    assert allowed is False
    assert "Max positions" in reason
