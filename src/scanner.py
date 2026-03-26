import time
import pandas as pd
from src.utils import fetch_data
from src.indicators import detect_fvg, detect_mss
from src.notifier import send_discord_alert  # 👈 Add this

# 🧠 The Bot's Memory: Remembers the last time it alerted an asset
last_alerted_time = {}

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
            df = detect_mss(df) 
            
            # Drop the active, unfinished forming candle (-1), 
            # and look only at the 3 most recently CLOSED candles
            latest_candles = df.iloc[-4:-1]
            
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
                signal_text = f"{recent_fvg} FVG (No MSS)"

            # ==========================================
            # ⚡ DISCORD ALERT TRIGGER
            # ==========================================
            # If it's an A+ signal, get the timestamp of the current candle
            if signal_text.startswith("🔥 A+"):
                current_candle_time = latest_candles.iloc[-1].name # Get the timestamp
                
                # Check if we ALREADY alerted for this exact candle
                if last_alerted_time.get(symbol) != current_candle_time:
                    # If not, send the alert and update the memory!
                    send_discord_alert(symbol, signal_text, round(df['close'].iloc[-1], 2), timeframe)
                    last_alerted_time[symbol] = current_candle_time

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
# ==========================================
# 🕒 THE GLOBAL DAEMON (Cloud Server Loop)
# ==========================================
if __name__ == "__main__":
    from datetime import datetime, timedelta, timezone

    def get_sleep_time(timeframe_hours=4):
        """Calculates exact seconds until the next 4H exchange candle closes."""
        now = datetime.now(timezone.utc)
        
        # Target the next 4-hour block (00:00, 04:00, 08:00, 12:00, 16:00, 20:00)
        next_hour = ((now.hour // timeframe_hours) + 1) * timeframe_hours
        
        if next_hour >= 24:
            next_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            next_time = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
        
        # ADD A 15-SECOND BUFFER (Lets Binance finalize the candle data)
        next_time = next_time + timedelta(seconds=15)
        
        return (next_time - now).total_seconds()

    print("Matrix Engine [V2] initialized. Synced to Global Exchange Clock...")
    
    while True:
        # 1. Calculate the exact math to the next 4-hour candle close
        seconds_to_sleep = get_sleep_time(timeframe_hours=4)
        next_wake = datetime.now() + timedelta(seconds=seconds_to_sleep)
        
        print(f"Engine sleeping. Next global scan scheduled for: {next_wake.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 2. Put the server to sleep
        time.sleep(seconds_to_sleep)
        
        # 3. WAKE UP and run the REAL Matrix Scan (which includes Discord alerts)
        print("Waking up! Executing Matrix Scan...")
        run_matrix_scan(SYMBOLS, timeframe='4h')