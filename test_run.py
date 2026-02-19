from src.utils import fetch_data
from src.indicators import detect_fvg

if __name__ == "__main__":
    print("--- Fetching Live Data ---")
    # Fetch 50 candles so we have enough history to find gaps
    df = fetch_data('BTC/USDT', '4h', 50)
    
    print("--- Scanning for FVGs ---")
    # This is the magic line where we apply your strategy
    df_with_signals = detect_fvg(df)
    
    # Let's filter to only show rows where an FVG was found
    found_gaps = df_with_signals.dropna(subset=['fvg_type'])
    
    if not found_gaps.empty:
        print("Found the following Fair Value Gaps:")
        print(found_gaps[['timestamp', 'fvg_type', 'fvg_top', 'fvg_bottom']])
    else:
        print("No FVGs found in the last 50 candles. Market is efficient right now!")