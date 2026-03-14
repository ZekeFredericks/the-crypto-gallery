import pandas as pd
from src.utils import fetch_data
from src.indicators import detect_fvg, detect_mss

def run_backtest(symbol="BTC/USDT", timeframe="1h", limit=5000):
    print(f"⏳ Fetching {limit} candles of historical data for {symbol}...")
    
    # 1. Fetch data and run our core Matrix indicators
    # Note: If your fetch_data uses yfinance, use "BTC-USD". If Binance, "BTC/USDT".
    df = fetch_data(symbol, timeframe, limit)
    
    if df.empty:
        print("❌ Failed to fetch data.")
        return

    print("🧠 Running Matrix Engine computations...")
    df = detect_fvg(df)
    df = detect_mss(df)

    print("⚔️ Simulating trades...\n")
    
    trades = []
    in_trade = False
    entry_price = 0
    sl = 0
    tp = 0
    trade_type = ""

    # RISK MANAGEMENT: 1.5% Risk, 3% Reward (1:2 R/R)
    RISK_PCT = 0.015
    REWARD_PCT = 0.03

    # Bot Memory (Mimicking your 3-candle Streamlit scanner)
    recent_fvg = None
    recent_mss = None
    fvg_timer = 0
    mss_timer = 0

    for index, row in df.iterrows():
        # =====================================
        # 1. CHECK IF WE HIT TAKE-PROFIT OR STOP-LOSS
        # =====================================
        if in_trade:
            if trade_type == "Long":
                if row['low'] <= sl:
                    trades.append({"result": "Loss", "type": "Long", "pnl": -RISK_PCT})
                    in_trade = False
                elif row['high'] >= tp:
                    trades.append({"result": "Win", "type": "Long", "pnl": REWARD_PCT})
                    in_trade = False
                    
            elif trade_type == "Short":
                if row['high'] >= sl:
                    trades.append({"result": "Loss", "type": "Short", "pnl": -RISK_PCT})
                    in_trade = False
                elif row['low'] <= tp:
                    trades.append({"result": "Win", "type": "Short", "pnl": REWARD_PCT})
                    in_trade = False
            continue # If we are in a trade, skip looking for new entries

        # =====================================
        # 2. HUNT FOR A+ CONFLUENCE (ENTRY LOGIC)
        # =====================================
        if not in_trade:
            # Update memory if we see a fresh signal
            if row.get('fvg_type') is not None and row.get('mitigated', False) == False:
                recent_fvg = row['fvg_type']
                fvg_timer = 30
                
            if row.get('mss_type') is not None:
                recent_mss = row['mss_type']
                mss_timer = 30

            # TRIGGER: If we have BOTH signals actively in memory
            if fvg_timer > 0 and mss_timer > 0:
                if recent_fvg == 'Bullish' and recent_mss == 'Bullish MSS':
                    in_trade = True
                    trade_type = "Long"
                    entry_price = row['close']
                    sl = entry_price * (1 - RISK_PCT)
                    tp = entry_price * (1 + REWARD_PCT)
                    recent_fvg = None # Wipe memory after entering
                    recent_mss = None
                    
                elif recent_fvg == 'Bearish' and recent_mss == 'Bearish MSS':
                    in_trade = True
                    trade_type = "Short"
                    entry_price = row['close']
                    sl = entry_price * (1 + RISK_PCT)
                    tp = entry_price * (1 - REWARD_PCT)
                    recent_fvg = None # Wipe memory after entering
                    recent_mss = None
            
            # Tick down the memory timers
            fvg_timer = max(0, fvg_timer - 1)
            mss_timer = max(0, mss_timer - 1)

    # =====================================
    # 3. CALCULATE THE BRUTAL TRUTH
    # =====================================
    wins = len([t for t in trades if t['result'] == 'Win'])
    losses = len([t for t in trades if t['result'] == 'Loss'])
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    print("="*40)
    print(f"📊 BACKTEST RESULTS: {symbol} (4hr Chart)")
    print(f"Tested over ~{len(df)} candles")
    print("="*40)
    print(f"Total Trades Taken : {total_trades}")
    print(f"Wins               : {wins}")
    print(f"Losses             : {losses}")
    print(f"Win Rate           : {win_rate:.2f}%")
    print("="*40)

if __name__ == "__main__":
    run_backtest(symbol="SOLUSDT", timeframe="4h", limit=5000)