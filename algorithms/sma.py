import pandas as pd
from .base import BaseStrategy

class SMACrossover(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.
    Buys when the short-term MA crosses above the long-term MA.
    Sells (or holds cash) when the short-term MA crosses below.
    """
    def __init__(self, short_window: int = 10, long_window: int = 50):
        super().__init__("SMA Crossover")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Calculate Moving Averages
        df['sma_short'] = df['close'].rolling(window=self.short_window, min_periods=1).mean()
        df['sma_long'] = df['close'].rolling(window=self.long_window, min_periods=1).mean()
        
        # Generate Signals: 1 for Buy (Long), 0 for Hold (Cash)
        # Using a simple Long-Only approach for Crypto Spot market simulation
        df['signal'] = 0
        df.loc[df['sma_short'] > df['sma_long'], 'signal'] = 1
        
        # 'position' is shifted by 1 because we trade on the next day's open or at today's close
        # Here we assume positional hold for the daily return duration
        df['position'] = df['signal'].shift(1).fillna(0)
        
        return df
