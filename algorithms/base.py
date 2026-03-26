from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """
    Base class for all quant algorithms.
    Any new algorithmic strategy should inherit from this class.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Takes OHLCV price DataFrame and returns DataFrame with added 'signal' column.
        signal: 1 (Buy/Long), -1 (Sell/Short), 0 (Hold/Flat)
        """
        pass
