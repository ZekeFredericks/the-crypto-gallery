import time
import pandas as pd
from src.utils import fetch_data
from src.indicators import detect_fvg, detect_mss

# ==========================================
# THE SETTINGS (Globals)
# ==========================================
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'GC=F', 'NQ=F', 'EURUSD=X', 'GBPUSD=X']

# ==========================================
# THE BLUEPRINTS (Functions)
# ==========================================

def run_matrix_scan(symbols, timeframe='4h'):
    """Returns a clean Pandas table for app.py to display"""
    results = []
    for symbol in symbols:
        try:
            # 1. Fetch data and run BOTH indicators
            df = fetch_data(symbol, timeframe, limit=100)
            df = detect_fvg(df)
            df = detect_mss(df)  # 👈 WE ADDED THIS LINE
            
            latest_candles = df.tail(3)
            
            # Track both signals temporarily
            recent_fvg = None
            recent_mss = None
            
            # 2. Scan the last 3 candles
            for index, row in latest_candles.iterrows():
                # Check for Fresh FVGs
                if row['fvg_type'] is not None and row['mitigated'] == False:
                    recent_fvg = row['fvg_type']
                
                # Check for Market Structure Shifts
                if row.get('mss_type') is not None:
                    recent_mss = row['mss_type']

            # 3. 🧠 THE CONFLUENCE LOGIC
            signal_text = "None"
            
            if recent_fvg == 'Bullish' and recent_mss == 'Bullish MSS':
                signal_text = "🔥 A+ Bullish"
            elif recent_fvg == 'Bearish' and recent_mss == 'Bearish MSS':
                signal_text = "🔥 A+ Bearish"
            elif recent_fvg is not None:
                # If there's an FVG but no MSS, it's just a regular setup
                signal_text = f"{recent_fvg} FVG (No MSS)"

            # 4. Append the final smart signal to the table
            results.append({
                "Asset": symbol,
                "Price": round(df['close'].iloc[-1], 2),
                "Active Signal (Last 3 Candles)": signal_text,
                "Status": "🟢 Online"
            })
            
        except Exception as e:
            results.append({
                "Asset": symbol,
                "Price": 0.0,
                "Active Signal (Last 3 Candles)": "N/A",
                "Status": f"🔴 Offline"
            })
            
    return pd.DataFrame(results)

# Blueprint B: Your original Terminal Scanner
def run_scanner():
    """Prints alerts directly to the terminal"""
    print("--- 🚀 STARTING GLOBAL SCAN ---")
    for symbol in SYMBOLS:
        try:
            df = fetch_data(symbol, '4h', 100)
            df = detect_fvg(df)
            df = detect_mss(df)
            
            latest = df.iloc[-1]
            print(f"Checking {symbol}...")
            
            if latest['fvg_type']:
                print(f"  ⚠️ ALERT: {latest['fvg_type']} FVG detected on {symbol}")
            if latest['mss_type']:
                print(f"  🔥 SIGNAL: {latest['mss_type']} detected on {symbol}")
                
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")

# ==========================================
if __name__ == "__main__":
    # This only runs if you type `python3 src/scanner.py`
    run_scanner()