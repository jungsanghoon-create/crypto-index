import ccxt
import pandas as pd

def fetch_ohlcv(exchange_name: str, symbol: str, timeframe: str = '1d', limit: int = 365) -> pd.DataFrame:
    """
    Fetch OHLCV data from the specified exchange using ccxt.
    exchange_name: "upbit", "bithumb", "coinone"
    symbol: "BTC/KRW", "ETH/KRW" etc.
    """
    try:
        # Initialize the exchange class dynamically
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class()
        
        # Determine symbol format (usually Base/Quote)
        if '/' not in symbol:
            symbol = f"{symbol}/KRW"
            
        # Fetch OHLCV
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        
        # Convert to Pandas DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('date', inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching data from {exchange_name} for {symbol}: {e}")
        return pd.DataFrame()
