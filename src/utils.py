import ccxt
import pandas as pd

def fetch_data(symbol, timeframe='4h', limit=100):
    """
    Connects to an exchange and fetches historical candle data.
    """
    # Initialize the exchange (Binance is great for free public data)
    exchange = ccxt.binance()

    # Fetch 'OHLCV' data: Open, High, Low, Close, Volume
    # For Gold/NAS100, we'll eventually use a different provider, 
    # but let's start with Crypto to verify the logic.
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    # Convert the list of lists into a clean Pandas Table (DataFrame)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Convert timestamp from milliseconds to readable dates
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    return df