"""
CoinGecko API client.

Pulls price/volume history for a given coin and a small set of top coins.
No API key required for the free public endpoints used here, but they are
rate-limited, so we cache responses in-memory per Streamlit run.
"""

from __future__ import annotations

import time
from typing import Any

import pandas as pd
import requests

BASE_URL = "https://api.coingecko.com/api/v3"

# Fixed top-10 list by market cap (reasonably stable; avoids an extra API call
# on every page load). If CoinGecko re-ranks something, just edit the list.
TOP_10_COINS: list[dict[str, str]] = [
    {"id": "bitcoin",     "symbol": "BTC",  "name": "Bitcoin"},
    {"id": "ethereum",    "symbol": "ETH",  "name": "Ethereum"},
    {"id": "tether",      "symbol": "USDT", "name": "Tether"},
    {"id": "binancecoin", "symbol": "BNB",  "name": "BNB"},
    {"id": "solana",      "symbol": "SOL",  "name": "Solana"},
    {"id": "ripple",      "symbol": "XRP",  "name": "XRP"},
    {"id": "cardano",     "symbol": "ADA",  "name": "Cardano"},
    {"id": "dogecoin",    "symbol": "DOGE", "name": "Dogecoin"},
    {"id": "polkadot",    "symbol": "DOT",  "name": "Polkadot"},
    {"id": "avalanche-2", "symbol": "AVAX", "name": "Avalanche"},
]

# Map UI labels -> CoinGecko "days" parameter.
TIMEFRAMES: dict[str, str] = {
    "1D":  "1",
    "7D":  "7",
    "30D": "30",
    "90D": "90",
    "1Y":  "365",
}


class CoinGeckoError(RuntimeError):
    """Raised when the CoinGecko API returns something unusable."""


def _get(path: str, params: dict[str, Any] | None = None, retries: int = 2) -> Any:
    """GET a CoinGecko endpoint with a small retry on rate limits."""
    url = f"{BASE_URL}{path}"
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 429:
                # Rate-limited — back off and try again.
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            last_err = exc
            time.sleep(1 + attempt)
    raise CoinGeckoError(f"CoinGecko request failed: {last_err}")


def fetch_market_chart(coin_id: str, days: str, vs_currency: str = "usd") -> pd.DataFrame:
    """
    Return a DataFrame indexed by timestamp with columns: price, volume.

    CoinGecko picks the candle granularity based on `days`:
      1     -> 5-minute data
      2-90  -> hourly
      >90   -> daily
    """
    data = _get(
        f"/coins/{coin_id}/market_chart",
        params={"vs_currency": vs_currency, "days": days},
    )
    prices = data.get("prices") or []
    volumes = data.get("total_volumes") or []
    if not prices:
        raise CoinGeckoError(f"No price data returned for {coin_id!r}")

    price_df = pd.DataFrame(prices, columns=["timestamp", "price"])
    vol_df = pd.DataFrame(volumes, columns=["timestamp", "volume"])

    df = price_df.merge(vol_df, on="timestamp", how="outer")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.sort_values("timestamp").set_index("timestamp")
    return df


def fetch_simple_stats(coin_id: str, vs_currency: str = "usd") -> dict[str, Any]:
    """Current price + 24h change for the header strip."""
    data = _get(
        "/simple/price",
        params={
            "ids": coin_id,
            "vs_currencies": vs_currency,
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
        },
    )
    stats = data.get(coin_id)
    if not stats:
        raise CoinGeckoError(f"No stats returned for {coin_id!r}")
    return {
        "price":        stats.get(vs_currency),
        "change_24h":   stats.get(f"{vs_currency}_24h_change"),
        "volume_24h":   stats.get(f"{vs_currency}_24h_vol"),
        "market_cap":   stats.get(f"{vs_currency}_market_cap"),
    }
