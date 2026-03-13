import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.utils import fetch_data
from src.indicators import detect_fvg, detect_mss, detect_liquidity
from src.scanner import run_matrix_scan

# 1. Page Configuration
st.set_page_config(page_title="The Crypto Gallery", layout="wide")
st.title("The Crypto Gallery: Signal Scanner")
st.markdown("---")
st.subheader("🖥️ The Matrix: Live Market Scanner")

# The assets the Matrix bot scans in the background
watchlist = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "GC=F", "NQ=F", "EURUSD=X", "GBPUSD=X"]

with st.spinner('Scanning the matrix for active setups...'):
    matrix_df = run_matrix_scan(watchlist, timeframe='4h')
    st.dataframe(matrix_df, use_container_width=True)

st.markdown("---")

# 2. Sidebar for User Inputs
# Add Forex to the drop-down list
symbol = st.sidebar.selectbox(
    "Select Asset", 
    ["BTC/USDT", "ETH/USDT", "SOL/USDT", "GC=F", "NQ=F", "EURUSD=X", "GBPUSD=X"]
)

# Add 15m to the timeframe list
timeframe = st.sidebar.selectbox(
    "Timeframe", 
    ["15m", "1h", "4h", "1d"], 
    index=1
)

# 3. Fetch and Process Data
df = fetch_data(symbol, timeframe, limit=100)
df = detect_fvg(df)
df = detect_mss(df)
levels = detect_liquidity(df)

# 4. Create the Chart
fig = go.Figure(data=[go.Candlestick(
    x=df['timestamp'],
    open=df['open'], high=df['high'],
    low=df['low'], close=df['close'],
    name="Price"
)])

# 5. Overlay FVG Boxes & 🎨Draw FVG Levels (with Mitigation Check)
for index, row in df.dropna(subset=['fvg_type']).iterrows():
            
            # 1. Determine Color AND the Right Edge (x_end)
            if row.get('mitigated', False) == True:
                # 👻 Ghost Gaps - Cut them off when they get filled!
                x_end = row['mitigated_timestamp']
                fill_color = "rgba(128, 128, 128, 0.2)"
                line_color = "rgba(128, 128, 128, 0.5)"
            elif row['fvg_type'] == 'Bullish':
                # 🟢 Fresh Bullish Gap - Stretch to current price
                x_end = df['timestamp'].iloc[-1]
                fill_color = "rgba(0, 255, 0, 0.2)"
                line_color = "rgba(0, 255, 0, 0.5)"
            else:
                # 🔴 Fresh Bearish Gap - Stretch to current price
                x_end = df['timestamp'].iloc[-1]
                fill_color = "rgba(255, 0, 0, 0.2)"
                line_color = "rgba(255, 0, 0, 0.5)"

            # 2. Draw the box using our new x_end logic
            fig.add_shape(
                type="rect",
                x0=row['timestamp'], y0=row['fvg_bottom'],
                x1=x_end, y1=row['fvg_top'],  # <--- THIS FIXES THE STRETCHING
                fillcolor=fill_color,
                line=dict(color=line_color, width=1),
                layer="below"
            )
        
# Fetch liquidity levels
liq = detect_liquidity(df)

# ==========================================
# 💧 DRAW THE LIQUIDITY POOLS (Swing Highs/Lows)
# ==========================================
# Draw the recent Buy-Side Liquidity (BSL) lines
for liq in levels.get('highs', []):
    fig.add_shape(
        type="line",
        x0=liq['timestamp'], y0=liq['price'],
        x1=df['timestamp'].iloc[-1], y1=liq['price'],
        line=dict(color="orange", width=2, dash="dash")
    )
    fig.add_annotation(
        x=df['timestamp'].iloc[-1], y=liq['price'],
        text="BSL (Swing High)", showarrow=False, yshift=10, font=dict(color="orange")
    )

# Draw the recent Sell-Side Liquidity (SSL) lines
for liq in levels.get('lows', []):
    fig.add_shape(
        type="line",
        x0=liq['timestamp'], y0=liq['price'],
        x1=df['timestamp'].iloc[-1], y1=liq['price'],
        line=dict(color="orange", width=2, dash="dash")
    )
    fig.add_annotation(
        x=df['timestamp'].iloc[-1], y=liq['price'],
        text="SSL (Swing Low)", showarrow=False, yshift=-10, font=dict(color="orange")
    )

# ==========================================
# ⚡ DRAW MARKET STRUCTURE SHIFTS (MSS)
# ==========================================
for index, row in df.dropna(subset=['mss_type']).iterrows():
    if row['mss_type'] == 'Bullish MSS':
        color = "lime"
        y_anchor = row['low']
        ay_offset = 30  # Arrow points up from below
        text = "⬆ Bullish MSS"
    else:
        color = "red"
        y_anchor = row['high']
        ay_offset = -30 # Arrow points down from above
        text = "⬇ Bearish MSS"
        
    fig.add_annotation(
        x=row['timestamp'], y=y_anchor,
        text=text, 
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor=color,
        font=dict(color=color, size=10), # <--- Removed the bad borderpad property
        ax=0, ay=ay_offset
    )

st.plotly_chart(fig, use_container_width=True)