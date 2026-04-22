# Crypto Price Dashboard

A Streamlit web dashboard that tracks the top-10 cryptocurrencies using live
data from the CoinGecko public API. Price, trading volume, moving averages,
and RSI, all in one interactive view.

> Personal project by **Sıla Kuzu** — built as part of my internship portfolio.
> Repo: [github.com/silakuuzu/crypto-price-dashboard](https://github.com/silakuuzu/crypto-price-dashboard)
> Türkçe açıklama için aşağıya bak: [Türkçe](#türkçe).

---

## Screenshot

<!-- Add a screenshot here (e.g. docs/screenshot.png) after running the app locally. -->

## Features

- Coin selector for the top 10 by market cap (BTC, ETH, SOL, BNB, XRP, ADA, DOGE, DOT, AVAX, USDT)
- Five timeframes: 1D / 7D / 30D / 90D / 1Y
- Header cards: live price, 24h change, 24h volume, market cap
- Price chart with toggleable SMA 20 / SMA 50 / EMA 20 overlays
- Volume bars in their own subplot
- RSI (14) subplot with 30/70 reference lines
- Expandable raw-data preview
- API responses cached for 1-5 minutes to stay inside CoinGecko's free rate limit

## Tech stack

| Layer            | Tool          |
| ---------------- | ------------- |
| Language         | Python 3.9+   |
| Web UI           | Streamlit     |
| Data processing  | pandas        |
| Charts           | Plotly        |
| HTTP client      | requests      |
| Data source      | CoinGecko API |

## Project layout

```
.
├── app.py            # Streamlit UI
├── api.py            # CoinGecko client (caching, retries, rate-limit handling)
├── indicators.py     # SMA / EMA / RSI calculations on pandas Series
├── requirements.txt
└── README.md
```

## Setup

Python 3.9 or newer is recommended.

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Streamlit opens the dashboard at `http://localhost:8501` in your browser.

## Notes

- The free CoinGecko endpoint is rate-limited. On a `CoinGecko request failed`
  error, wait a few seconds and re-run; the in-app cache reduces hits on
  subsequent interactions.
- CoinGecko picks candle granularity from the requested range: 1 day = 5-minute
  candles, 2–90 days = hourly, 90+ days = daily. SMA / RSI windows are measured
  in *candles*, not days, so on shorter timeframes the moving averages cover a
  smaller wall-clock window.

## What I learned

- Calling a public REST API, parsing JSON, and handling errors and rate limits
- Implementing indicators (SMA, EMA, Wilder-smoothed RSI) on pandas Series
- Splitting an app into modules: API client, business logic, UI
- Rapid UI prototyping with Streamlit caching and state
- Combining multiple Plotly traces in a single figure with shared axes

## Roadmap

- MACD and Bollinger Bands indicators
- Price alerts (threshold-based)
- Coin comparison mode (overlay two series)
- Lightweight portfolio tracker

---

<a id="türkçe"></a>

## Türkçe

CoinGecko ücretsiz API'sinden anlık veri çeken, ilk 10 kripto para için fiyat,
işlem hacmi, hareketli ortalamalar ve RSI gösteren Streamlit tabanlı bir web
panosu.

### Özellikler

- 10 coin için seçim menüsü (BTC, ETH, SOL, BNB, XRP, ADA, DOGE, DOT, AVAX, USDT)
- 5 zaman aralığı: 1 gün / 7 gün / 30 gün / 90 gün / 1 yıl
- Üstte anlık fiyat, 24 saatlik değişim, hacim ve piyasa değeri kartları
- Fiyat grafiğinde açılıp kapanabilen SMA 20, SMA 50, EMA 20 çizgileri
- Ayrı panelde hacim grafiği ve RSI (14) göstergesi (30/70 referans çizgileriyle)
- Ham veri tablosu (açılır-kapanır)
- API yanıtları 1–5 dakika önbelleğe alınıyor — ücretsiz limit içinde kalır

### Kurulum

```bash
pip install -r requirements.txt
```

### Çalıştırma

```bash
streamlit run app.py
```

Uygulama `http://localhost:8501` adresinde açılır.

### Neler öğrendim

- REST API çağırma, JSON ayrıştırma, hata yönetimi ve rate-limit mantığı
- Pandas ile zaman serisi işleme (hareketli ortalama, RSI)
- Modüler yapı: API katmanı, iş mantığı ve arayüz ayrı dosyalarda
- Streamlit ile hızlı prototipleme, önbellekleme (caching)
- Plotly'de birden fazla grafiği tek figürde birleştirme (subplot)

### Sonraki adımlar

MACD ve Bollinger Bantları, fiyat uyarıları, coin karşılaştırma ekranı ve
portföy takibi planlanıyor.

---

**Contact** — silakuuzu@gmail.com
