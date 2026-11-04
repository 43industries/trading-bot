# Trading Bot (Freqtrade)

Crypto spot bot built on [Freqtrade](https://github.com/freqtrade/freqtrade) + CCXT.

**Defaults:** Binance spot · `BTC/USDT` + `ETH/USDT` + `XRP/USDT` + `SOL/USDT` · `1h` · **dry-run** · strategy `FreqaiSpotStrategy` (FreqAI / LightGBM)

This repo does **not** guarantee profit. You must pass the gates below before live trading.

## Setup

```powershell
cd freqtrade
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip wheel
python -m pip install -e .
python -m pip install -r requirements-freqai.txt
freqtrade install-ui
Copy-Item user_data\config.example.json user_data\config.json
# Edit user_data\config.json (API password, optional exchange keys)
freqtrade --version
```

## Commands

### Download history

```powershell
freqtrade download-data --config user_data/config.json --exchange binance --pairs BTC/USDT ETH/USDT XRP/USDT SOL/USDT --timeframes 1h 4h --timerange 20250101- --userdir user_data
```

### Train / backtest (FreqAI)

```powershell
freqtrade backtesting --config user_data/config.json --strategy FreqaiSpotStrategy --freqaimodel LightGBMRegressor --timerange 20250901- --userdir user_data
```

Models are written under `user_data/models/43industries-spot-v1/`.

### Dry-run (paper trade with live retrain)

```powershell
freqtrade trade --config user_data/config.json --strategy FreqaiSpotStrategy --freqaimodel LightGBMRegressor --userdir user_data
```

Stop with `Ctrl+C`. Keep `dry_run: true` in `user_data/config.json` until gates pass.

### Web UI (43_industries bot)

Enabled on localhost. With the bot running, open:

**http://127.0.0.1:8080/**

- Bot name: `43_industries bot`
- Username: `freqtrader`
- Password: `SuperSecurePassword`

Change those in `user_data/config.json` → `api_server` / `bot_name` before exposing beyond this PC.

### Optional Telegram

Set `telegram.enabled`, `token`, and `chat_id` in config.

## Profitability gates (must pass before live)

| Gate | Pass criteria |
|------|----------------|
| Fees | Backtest uses realistic fees (Binance spot ~0.1% unless you have VIP rates) |
| Expectancy | Net profit **after fees** > 0 over the full test window |
| Sample size | Enough trades to judge (prefer dozens+, not a handful) |
| Drawdown | Max drawdown within your limit (suggested ≤ 20%) |
| Dry-run | Paper trade 1–2 weeks; live results should not contradict backtest direction |

If a gate fails: change strategy parameters, change strategy, or do not go live.

### Latest FreqAI backtest (`FreqaiSpotStrategy` + LightGBM, Sep–Nov 2025)

| Metric | Result | Gate |
|--------|--------|------|
| Trades | 78 (win rate 74.4%) | Pass (sample OK) |
| Total profit | **-0.13%** (-1.3 USDT) | **Fail** (expectancy) |
| Profit factor | 0.98 | **Fail** (< 1) |
| Per pair | XRP +0.46% · BTC +0.31% · SOL +0.03% · ETH **-0.92%** | — |
| Models | ~100 rolling trains under `user_data/models/43industries-spot-v1/` | — |

**Verdict: do not go live.** FreqAI is enabled and trained; still slightly negative after fees. Keep dry-run; next tune features/thresholds or drop weak pairs.

### Active brain (FreqAI)

- Strategy: `FreqaiSpotStrategy` — predicts mean forward return (`&-s_close`)
- Model: `LightGBMRegressor`, retrain every 24h in dry/live
- Features: RSI/MFI/ADX/SMA/EMA/BB/ROC/volume on 1h+4h, with BTC/ETH correlation features
- Entry: `do_predict==1` and predicted return > 1%
- Exit: predicted return < 0, plus ROI / -6% stop
- Rule baselines kept: `EmaRsiStrategy.py`, `EmaRsiV2Strategy.py`

## Live checklist (later)

1. All gates above pass.
2. Create Binance API key with **trade only** (no withdraw).
3. Put key/secret in config (never commit them).
4. Set a tiny `stake_amount`.
5. Set `"dry_run": false` only when ready.
6. Watch the first sessions closely; keep max open trades low.

## Project layout

```
trading bot/
  README.md
  .gitignore
  freqtrade/
    user_data/
      config.json
      strategies/
        FreqaiSpotStrategy.py  # active FreqAI brain
        EmaRsiV2Strategy.py
        EmaRsiStrategy.py
      models/                  # trained FreqAI models (local, gitignored)
```

