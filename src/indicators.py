import pandas as pd

def detect_fvg(df, min_size_pct=0.0015):
    """
    Detects Institutional-Sized Fair Value Gaps (FVGs) and checks for mitigation.
    min_size_pct = 0.0015 means the gap must be at least 0.15% of the price.
    """
    df['fvg_type'] = None
    df['fvg_top'] = None
    df['fvg_bottom'] = None
    df['mitigated'] = False
    df['mitigated_timestamp'] = pd.NaT

    # 1. Find the Gaps (WITH THE NEW SIZE FILTER)
    for i in range(2, len(df)):
        # Bullish FVG
        if df['high'].iloc[i-2] < df['low'].iloc[i]:
            gap_bottom = df['high'].iloc[i-2]
            gap_top = df['low'].iloc[i]
            
            # 🔥 THE MATH: How big is this gap relative to the price?
            gap_size = (gap_top - gap_bottom) / gap_bottom
            
            # 🛡️ THE FILTER: Only flag it if it's a whale-sized gap
            if gap_size >= min_size_pct:
                df.at[df.index[i], 'fvg_type'] = 'Bullish'
                df.at[df.index[i], 'fvg_bottom'] = gap_bottom
                df.at[df.index[i], 'fvg_top'] = gap_top
            
        # Bearish FVG
        elif df['low'].iloc[i-2] > df['high'].iloc[i]:
            gap_top = df['low'].iloc[i-2]
            gap_bottom = df['high'].iloc[i]
            
            # 🔥 THE MATH
            gap_size = (gap_top - gap_bottom) / gap_bottom
            
            # 🛡️ THE FILTER
            if gap_size >= min_size_pct:
                df.at[df.index[i], 'fvg_type'] = 'Bearish'
                df.at[df.index[i], 'fvg_top'] = gap_top
                df.at[df.index[i], 'fvg_bottom'] = gap_bottom

    # 2. The Time Machine (Mitigation Check - Unchanged)
    for i in range(2, len(df)):
        if df['fvg_type'].iloc[i] == 'Bullish':
            for j in range(i + 1, len(df)):
                if df['low'].iloc[j] <= df['fvg_top'].iloc[i]:
                    df.at[df.index[i], 'mitigated'] = True
                    df.at[df.index[i], 'mitigated_timestamp'] = df['timestamp'].iloc[j]
                    break

        elif df['fvg_type'].iloc[i] == 'Bearish':
            for j in range(i + 1, len(df)):
                if df['high'].iloc[j] >= df['fvg_bottom'].iloc[i]:
                    df.at[df.index[i], 'mitigated'] = True
                    df.at[df.index[i], 'mitigated_timestamp'] = df['timestamp'].iloc[j]
                    break

    return df

def detect_mss(df, window=5):
    """
    Detects TRUE Market Structure Shifts (MSS).
    Only flags a shift when the trend actually reverses, ignoring continuous breakouts.
    """
    df['mss_type'] = None
    df['mss_line'] = None  # <--- NEW: Create a column to remember the broken line
    current_trend = None  # The memory of the bot
    
    for i in range(window, len(df)):
        prev_high = df['high'].iloc[i-window:i].max()
        prev_low = df['low'].iloc[i-window:i].min()

        # 1. Check for Bullish Break
        if df['close'].iloc[i] > prev_high:
            # ONLY flag it if the trend wasn't already Bullish
            if current_trend != 'Bullish':
                df.at[df.index[i], 'mss_type'] = 'Bullish MSS'
                df.at[df.index[i], 'mss_line'] = prev_high  # <--- NEW: Save the ceiling price
                current_trend = 'Bullish'  # Update the memory
                
        # 2. Check for Bearish Break
        elif df['close'].iloc[i] < prev_low:
            # ONLY flag it if the trend wasn't already Bearish
            if current_trend != 'Bearish':
                df.at[df.index[i], 'mss_type'] = 'Bearish MSS'
                df.at[df.index[i], 'mss_line'] = prev_low  # <--- NEW: Save the floor price
                current_trend = 'Bearish'  # Update the memory

    return df

def detect_liquidity(df, window=5):
    """
    Identifies Swing Highs and Swing Lows as Liquidity Pools.
    A Swing High is the highest point within a 'window' of candles.
    """
    swing_highs = []
    swing_lows = []

    # Loop through the data, leaving room on the left and right for the 'window'
    for i in range(window, len(df) - window):
        
        # 1. Look at a small slice of candles around our current candle
        local_window = df.iloc[i-window : i+window+1]
        
        # 2. Check for Buy-Side Liquidity (Swing High)
        if df['high'].iloc[i] == local_window['high'].max():
            swing_highs.append({
                'timestamp': df['timestamp'].iloc[i],
                'price': df['high'].iloc[i]
            })
            
        # 3. Check for Sell-Side Liquidity (Swing Low)
        elif df['low'].iloc[i] == local_window['low'].min():
            swing_lows.append({
                'timestamp': df['timestamp'].iloc[i],
                'price': df['low'].iloc[i]
            })

    # Return the 3 most recent swing highs and lows so the chart doesn't get cluttered
    return {
        'highs': swing_highs[-3:], 
        'lows': swing_lows[-3:]
    }