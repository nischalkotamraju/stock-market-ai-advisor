import pandas as pd
import numpy as np
from datetime import datetime

def calculate_roi(initial_value: float, current_value: float) -> float:
    roi = ((current_value - initial_value) / initial_value) * 100
    return round(roi, 2)

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    excess_returns = returns - risk_free_rate
    return np.sqrt(252) * (excess_returns.mean() / returns.std())

def calculate_volatility(returns: pd.Series) -> float:
    return returns.std() * np.sqrt(252) * 100

def track_profit_loss(positions: pd.DataFrame) -> pd.Series:
    return positions['current_value'] - positions['initial_investment']

def calculate_sector_diversity(positions: pd.DataFrame) -> pd.Series:
    return (positions.groupby('sector')['current_value']
            .sum()
            .div(positions['current_value'].sum()) * 100)