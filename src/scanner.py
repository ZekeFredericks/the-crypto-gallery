from src.utils import fetch_data
from src.indicators import detect_fvg, detect_mss
import time

# List of assets you want to track
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'] 

def run_scanner():
    print("--- 🚀 STARTING GLOBAL SCAN ---")
    for symbol in SYMBOLS:
        try:
            # 1. Get Data
            df = fetch_data(symbol, '4h', 100)
            
            # 2. Apply Indicators
            df = detect_fvg(df)
            df = detect_mss(df)
            
            # 3. Check the LATEST candle for signals
            latest = df.iloc[-1]
            
            print(f"Checking {symbol}...")
            if latest['fvg_type']:
                print(f"  ⚠️ ALERT: {latest['fvg_type']} FVG detected on {symbol}")
            if latest['mss_type']:
                print(f"  🔥 SIGNAL: {latest['mss_type']} detected on {symbol}")
                
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")

if __name__ == "__main__":
    run_scanner()