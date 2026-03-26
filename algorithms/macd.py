import pandas as pd
from .base import BaseStrategy

class MACDCrossover(BaseStrategy):
    """
    Moving Average Convergence Divergence (MACD) Strategy.
    Buys when the MACD line crosses above the Signal line.
    Sells (or holds cash) when the MACD crosses below the Signal line.
    """
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__("MACD Crossover")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Calculate MACD
        ema_fast = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=self.signal_period, adjust=False).mean()
        
        # Generate Signals: 1 for Buy (Long), 0 for Hold (Cash)
        df['signal'] = 0
        df.loc[df['macd'] > df['macd_signal'], 'signal'] = 1
        
        df['position'] = df['signal'].shift(1).fillna(0)
        
        return df
