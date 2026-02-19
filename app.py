import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.utils import fetch_data
from src.indicators import detect_fvg, detect_mss, detect_liquidity

# 1. Page Configuration
st.set_page_config(page_title="The Crypto Gallery", layout="wide")
st.title("🎨 The Crypto Gallery: Signal Scanner")

# 2. Sidebar for User Inputs
symbol = st.sidebar.selectbox("Select Asset", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"])

# 3. Fetch and Process Data
df = fetch_data(symbol, timeframe, limit=100)
df = detect_fvg(df)
df = detect_mss(df)

# 4. Create the Chart
fig = go.Figure(data=[go.Candlestick(
    x=df['timestamp'],
    open=df['open'], high=df['high'],
    low=df['low'], close=df['close'],
    name="Price"
)])

# 5. Overlay FVG Boxes
for i in range(len(df)):
    if df['fvg_type'].iloc[i] == 'Bullish':
        fig.add_shape(type="rect",
            x0=df['timestamp'].iloc[i], y0=df['fvg_bottom'].iloc[i],
            x1=df['timestamp'].iloc[i+2] if i+2 < len(df) else df['timestamp'].iloc[-1], 
            y1=df['fvg_top'].iloc[i],
            fillcolor="green", opacity=0.3, line_width=0)
    elif df['fvg_type'].iloc[i] == 'Bearish':
        fig.add_shape(type="rect",
            x0=df['timestamp'].iloc[i], y0=df['fvg_bottom'].iloc[i],
            x1=df['timestamp'].iloc[i+2] if i+2 < len(df) else df['timestamp'].iloc[-1], 
            y1=df['fvg_top'].iloc[i],
            fillcolor="red", opacity=0.3, line_width=0)
        
# Fetch liquidity levels
liq = detect_liquidity(df)

# Draw Horizontal Liquidity Lines
fig.add_hline(y=liq['high_liq'], line_dash="dash", line_color="orange", annotation_text="Buy Side Liquidity")
fig.add_hline(y=liq['low_liq'], line_dash="dash", line_color="orange", annotation_text="Sell Side Liquidity")

st.plotly_chart(fig, use_container_width=True)