"""
Crypto Dashboard — Streamlit app.

Run with:
    streamlit run app.py

Pick a coin + timeframe from the sidebar; the main panel renders a price
chart with moving averages, a volume chart, and an RSI subplot.
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from api import (
    TOP_10_COINS,
    TIMEFRAMES,
    CoinGeckoError,
    fetch_market_chart,
    fetch_simple_stats,
)
from indicators import attach_indicators


# ---------- Page setup ----------

st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="CD",
    layout="wide",
)


# ---------- Cached data loaders ----------

@st.cache_data(ttl=300, show_spinner=False)
def load_chart(coin_id: str, days: str):
    """Price + volume history, cached for 5 minutes."""
    return fetch_market_chart(coin_id, days)


@st.cache_data(ttl=60, show_spinner=False)
def load_stats(coin_id: str):
    """Current price / 24h change, cached for 1 minute."""
    return fetch_simple_stats(coin_id)


# ---------- Sidebar controls ----------

st.sidebar.title("Crypto Dashboard")
st.sidebar.caption("Data: CoinGecko public API")

coin_labels = [f"{c['name']} ({c['symbol']})" for c in TOP_10_COINS]
coin_choice = st.sidebar.selectbox("Coin", coin_labels, index=0)
selected_coin = TOP_10_COINS[coin_labels.index(coin_choice)]

timeframe_label = st.sidebar.radio(
    "Timeframe",
    list(TIMEFRAMES.keys()),
    index=2,  # default 30D
    horizontal=True,
)
days = TIMEFRAMES[timeframe_label]

st.sidebar.markdown("---")
st.sidebar.subheader("Indicators")
show_sma20 = st.sidebar.checkbox("SMA 20",  value=True)
show_sma50 = st.sidebar.checkbox("SMA 50",  value=True)
show_ema20 = st.sidebar.checkbox("EMA 20",  value=False)
show_rsi   = st.sidebar.checkbox("RSI (14)", value=True)


# ---------- Main panel ----------

st.title(f"{selected_coin['name']} ({selected_coin['symbol']})")

# --- Header stats ---
try:
    stats = load_stats(selected_coin["id"])
except CoinGeckoError as exc:
    st.error(f"Could not load stats: {exc}")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Price (USD)", f"${stats['price']:,.2f}" if stats["price"] else "—")
col2.metric(
    "24h Change",
    f"{stats['change_24h']:.2f}%" if stats["change_24h"] is not None else "—",
    delta=f"{stats['change_24h']:.2f}%" if stats["change_24h"] is not None else None,
)
col3.metric(
    "24h Volume",
    f"${stats['volume_24h']:,.0f}" if stats["volume_24h"] else "—",
)
col4.metric(
    "Market Cap",
    f"${stats['market_cap']:,.0f}" if stats["market_cap"] else "—",
)

st.markdown("---")

# --- Chart ---
try:
    raw = load_chart(selected_coin["id"], days)
except CoinGeckoError as exc:
    st.error(f"Could not load chart data: {exc}")
    st.stop()

df = attach_indicators(raw)

# Decide subplot layout based on whether RSI is turned on.
if show_rsi:
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("Price", "Volume", "RSI (14)"),
    )
else:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.75, 0.25],
        subplot_titles=("Price", "Volume"),
    )

# Price line
fig.add_trace(
    go.Scatter(
        x=df.index, y=df["price"],
        name=f"{selected_coin['symbol']} Price",
        line=dict(width=2),
    ),
    row=1, col=1,
)

# Moving averages overlaid on price
if show_sma20:
    fig.add_trace(
        go.Scatter(x=df.index, y=df["SMA_20"], name="SMA 20",
                   line=dict(width=1, dash="dot")),
        row=1, col=1,
    )
if show_sma50:
    fig.add_trace(
        go.Scatter(x=df.index, y=df["SMA_50"], name="SMA 50",
                   line=dict(width=1, dash="dash")),
        row=1, col=1,
    )
if show_ema20:
    fig.add_trace(
        go.Scatter(x=df.index, y=df["EMA_20"], name="EMA 20",
                   line=dict(width=1)),
        row=1, col=1,
    )

# Volume bars
fig.add_trace(
    go.Bar(
        x=df.index, y=df["volume"],
        name="Volume",
        marker=dict(color="rgba(100,149,237,0.6)"),
        showlegend=False,
    ),
    row=2, col=1,
)

# RSI subplot (if enabled)
if show_rsi:
    fig.add_trace(
        go.Scatter(x=df.index, y=df["RSI_14"], name="RSI 14",
                   line=dict(width=1.5, color="purple")),
        row=3, col=1,
    )
    # Overbought / oversold reference lines
    fig.add_hline(y=70, line=dict(color="red", dash="dash", width=1),
                  row=3, col=1)
    fig.add_hline(y=30, line=dict(color="green", dash="dash", width=1),
                  row=3, col=1)
    fig.update_yaxes(range=[0, 100], row=3, col=1)

fig.update_layout(
    height=720 if show_rsi else 560,
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    margin=dict(l=10, r=10, t=40, b=10),
)
fig.update_yaxes(title_text="USD", row=1, col=1)
fig.update_yaxes(title_text="Volume", row=2, col=1)

st.plotly_chart(fig, use_container_width=True)


# --- Data preview ---
with st.expander("Show raw data"):
    st.dataframe(df.tail(200), use_container_width=True)

st.caption(
    f"Timeframe: {timeframe_label}  •  "
    f"{len(df)} data points  •  "
    "Auto-refreshes every 5 minutes"
)
