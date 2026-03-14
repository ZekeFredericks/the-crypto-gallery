import requests
import pandas as pd
import time

def fetch_data(symbol="BTCUSDT", timeframe="1h", limit=5000):
    """Fetches deep historical data directly from the Binance REST API."""
    print(f"📡 Downloading {limit} candles from Binance for {symbol}...")
    
    url = "https://api.binance.com/api/v3/klines"
    all_candles = []
    end_time = None
    
    # Binance only allows 1000 candles per request, so we loop to get deep history
    while len(all_candles) < limit:
        # Request up to 1000 candles at a time
        batch_size = min(1000, limit - len(all_candles))
        params = {
            "symbol": symbol.replace("/", "").replace("-", ""), # Formats to BTCUSDT
            "interval": timeframe,
            "limit": batch_size
        }
        
        # If we already have some candles, ask for the ones that came BEFORE them
        if end_time:
            params["endTime"] = end_time
            
        response = requests.get(url, params=params)
        data = response.json()
        
        if not data or type(data) is dict: # API hit an error or ran out of data
            print("⚠️ Binance API stopped returning data.")
            break
            
        # Add the new batch of candles to the FRONT of our list
        all_candles = data + all_candles 
        
        # Set the end_time for the next loop to 1 millisecond before our oldest candle
        end_time = data[0][0] - 1 
        time.sleep(0.1) # Be polite to the Binance servers so we don't get banned
        
    if not all_candles:
        return pd.DataFrame()
        
    # Format the raw Binance data into our clean Matrix format
    df = pd.DataFrame(all_candles, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
    ])
    
    # Convert timestamps to actual dates
    # Convert timestamps to actual dates, keep it as a column AND an index
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', drop=False, inplace=True) # drop=False keeps the column!
    
    # Convert string prices to decimals
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
        
    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]