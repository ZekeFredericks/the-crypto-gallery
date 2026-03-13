import ccxt
import yfinance as yf
import pandas as pd
import requests  # 👈 New tool to spoof the browser

def fetch_data(symbol, timeframe='1h', limit=100):
    """
    Smart data fetcher. 
    Routes Crypto to Binance (CCXT) and Legacy/Forex to Yahoo Finance.
    """
    if "/" in symbol:
        # 🟢 CRYPTO PIPELINE (Binance)
        exchange = ccxt.binance()
        bars = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
        
    else:
        # 🔵 LEGACY & FOREX PIPELINE (Yahoo Finance)
        yf_interval = timeframe
        if timeframe == '4h':
            yf_interval = '1h' 
            
        period = '60d' if yf_interval in ['15m', '1h'] else '1y'

        # 🕵️‍♂️ THE TRENCH COAT (User-Agent Spoofing)
        # We tell Yahoo Finance that we are a normal Google Chrome browser.
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })

        # Pass the disguised session to yfinance
        ticker = yf.Ticker(symbol, session=session)
        df = ticker.history(interval=yf_interval, period=period)
        
        if df.empty:
            raise ValueError(f"Yahoo Finance returned no data for {symbol}")

        # Clean up the Yahoo Finance table to match our Crypto table perfectly
        df = df.reset_index()
        time_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
        df.rename(columns={
            time_col: 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        return df.tail(limit).reset_index(drop=True)