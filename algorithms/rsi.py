import pandas as pd
import numpy as np
from .base import BaseStrategy

class RSIMomentum(BaseStrategy):
    """
    Relative Strength Index (RSI) Strategy.
    Buys (Long) when RSI falls below the oversold threshold (e.g., 30).
    Sells (Cash) when RSI rises above the overbought threshold (e.g., 70).
    """
    def __init__(self, period: int = 14, overbought: int = 70, oversold: int = 30):
        super().__init__("RSI Momentum")
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Generate Signals: 1 for Buy (Long), 0 for Hold (Cash)
        df['signal'] = np.nan
        df.loc[df['rsi'] < self.oversold, 'signal'] = 1
        df.loc[df['rsi'] > self.overbought, 'signal'] = 0
        
        # Forward fill the signals so we hold the position between crosses
        df['signal'] = df['signal'].ffill().fillna(0)
        
        df['position'] = df['signal'].shift(1).fillna(0)
        
        return df
