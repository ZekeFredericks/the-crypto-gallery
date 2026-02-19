import pandas as pd

def detect_fvg(df):
    """
    Detects Bullish and Bearish Fair Value Gaps.
    - Bullish: Gap between Candle 1 High and Candle 3 Low
    - Bearish: Gap between Candle 1 Low and Candle 3 High
    """
    # Create empty columns for our results
    df['fvg_type'] = None
    df['fvg_top'] = None
    df['fvg_bottom'] = None

    # We loop through the data starting at index 2 (the 3rd candle)
    for i in range(2, len(df)):
        
        # 1. BULLISH FVG (Buying Imbalance)
        # Condition: High of 2 candles ago is LOWER than Low of current candle
        if df['high'].iloc[i-2] < df['low'].iloc[i]:
            df.at[df.index[i-1], 'fvg_type'] = 'Bullish'
            df.at[df.index[i-1], 'fvg_top'] = df['low'].iloc[i]
            df.at[df.index[i-1], 'fvg_bottom'] = df['high'].iloc[i-2]

        # 2. BEARISH FVG (Selling Imbalance)
        # Condition: Low of 2 candles ago is HIGHER than High of current candle
        elif df['low'].iloc[i-2] > df['high'].iloc[i]:
            df.at[df.index[i-1], 'fvg_type'] = 'Bearish'
            df.at[df.index[i-1], 'fvg_top'] = df['low'].iloc[i-2]
            df.at[df.index[i-1], 'fvg_bottom'] = df['high'].iloc[i]

    return df

def detect_mss(df, window=5):
    """
    Detects Market Structure Shifts (MSS).
    Bullish MSS: Current Close > Highest High of previous 'window' candles.
    Bearish MSS: Current Close < Lowest Low of previous 'window' candles.
    """
    df['mss_type'] = None

    for i in range(window, len(df)):
        # Calculate the previous peak/trough (excluding current candle)
        prev_high = df['high'].iloc[i-window:i].max()
        prev_low = df['low'].iloc[i-window:i].min()

        # Check for Bullish Shift
        if df['close'].iloc[i] > prev_high:
            df.at[df.index[i], 'mss_type'] = 'Bullish MSS'
            
        # Check for Bearish Shift
        elif df['close'].iloc[i] < prev_low:
            df.at[df.index[i], 'mss_type'] = 'Bearish MSS'

    return df

def detect_liquidity(df):
    """
    Identifies major liquidity levels (Swing Highs/Lows).
    For now, we'll mark the highest and lowest price in the current view.
    """
    levels = {
        'high_liq': df['high'].max(),
        'low_liq': df['low'].min()
    }
    return levels