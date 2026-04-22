"""
Technical indicators — SMA, EMA, and RSI — built on pandas.

Each function takes a price Series and returns a Series of the same length,
with leading NaNs where the window hasn't filled yet.
"""

from __future__ import annotations

import pandas as pd


def sma(prices: pd.Series, window: int) -> pd.Series:
    """Simple moving average over `window` periods."""
    return prices.rolling(window=window, min_periods=window).mean()


def ema(prices: pd.Series, window: int) -> pd.Series:
    """Exponential moving average — more weight on recent prices."""
    return prices.ewm(span=window, adjust=False, min_periods=window).mean()


def rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """
    Relative Strength Index using Wilder's smoothing.

    Values range 0-100:
      > 70 -> overbought
      < 30 -> oversold
    """
    delta = prices.diff()

    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)

    # Wilder's smoothing == EMA with alpha = 1/window
    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()

    rs = avg_gain / avg_loss
    rsi_series = 100 - (100 / (1 + rs))

    # When avg_loss is 0 the series goes to 100; when both are 0 pandas gives NaN.
    rsi_series = rsi_series.where(avg_loss != 0, 100.0)
    return rsi_series


def attach_indicators(
    df: pd.DataFrame,
    sma_windows: tuple[int, ...] = (20, 50),
    ema_windows: tuple[int, ...] = (20,),
    rsi_window: int = 14,
    price_col: str = "price",
) -> pd.DataFrame:
    """
    Return a copy of `df` with SMA/EMA/RSI columns appended.

    Column names: SMA_20, SMA_50, EMA_20, RSI_14, etc.
    """
    out = df.copy()
    for w in sma_windows:
        out[f"SMA_{w}"] = sma(out[price_col], w)
    for w in ema_windows:
        out[f"EMA_{w}"] = ema(out[price_col], w)
    out[f"RSI_{rsi_window}"] = rsi(out[price_col], rsi_window)
    return out
