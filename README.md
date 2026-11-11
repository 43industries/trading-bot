# Trading Bot (Freqtrade)

Crypto spot bot built on [Freqtrade](https://github.com/freqtrade/freqtrade) + CCXT.

**Defaults:** Binance spot · `BTC/USDT` + `XRP/USDT` + `SOL/USDT` · `1h` · **dry-run** · strategy `FreqaiSpotStrategy` (FreqAI / LightGBM v2)

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
freqtrade download-data --config user_data/config.json --exchange binance --pairs BTC/USDT XRP/USDT SOL/USDT --timeframes 1h 4h --timerange 20250101- --userdir user_data
```

### Train / backtest (FreqAI)

```powershell
freqtrade backtesting --config user_data/config.json --strategy FreqaiSpotStrategy --freqaimodel LightGBMRegressor --timerange 20250901- --userdir user_data --enable-protections
```

Models are written under `user_data/models/43industries-spot-v2/`.

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

### Latest FreqAI backtest (brain+risk v2, Sep–Nov 2025)

| Metric | V2 result | Prior v1 | Gate |
|--------|-----------|----------|------|
| Trades | 18 (win ~89%) | 78 | **Fail** (sample < 40) |
| Total profit | **+0.39%** (+3.91 USDT) | -0.13% | Pass |
| Profit factor | **2.07** | 0.98 | Pass |
| Max drawdown | 0.31% | — | Pass (≤ 15%) |
| Per pair | SOL +0.25% · XRP +0.10% · BTC +0.04% | ETH was -0.92% (dropped) | — |
| Risk | stake 50, max 2 trades, StoplossGuard + MaxDrawdown | — | — |

**Verdict: do not go live yet.** Expectancy and PF improved, but trade count is thin. Keep dry-run; collect more paper trades before live.

### Classifier experiment (failed — not promoted)

Walk-forward Jun–Nov 2025 with `FreqaiSpotClassifierStrategy` + `LightGBMClassifier` (`43industries-spot-clf-v1`): up/down label over 12h, same 4h EMA filter and v2 risk.

| Metric | Classifier | Gate |
|--------|------------|------|
| Trades | 185 (win 55%) | Pass (≥ 40) |
| Total profit | **-2.12%** (−21.18 USDT) | **Fail** |
| Profit factor | **0.62** | **Fail** |
| Expectancy | −0.11 | **Fail** |
| Max drawdown | 2.39% | Pass (≤ 15%) |
| Per pair | BTC −0.05% · XRP −0.65% · SOL −1.41% | — |

Worse expectancy/PF than regression v2 → **dry-run stays on regression v2**. Classifier strategy kept for experiments only.

```powershell
freqtrade backtesting --config user_data/config.json --strategy FreqaiSpotClassifierStrategy --freqaimodel LightGBMClassifier --timerange 20250601-20251104 --userdir user_data --enable-protections
```

### Active brain (FreqAI v2) — dry-run

- Strategy: `FreqaiSpotStrategy` — predicts mean forward return (`&-s_close`)
- Model: `LightGBMRegressor`, identifier `43industries-spot-v2`, retrain every 24h
- Features: RSI/MFI/ADX/SMA/EMA/BB/ROC/volume on 1h+4h, BTC/ETH corr features
- Entry: `do_predict==1`, pred > **1.5%**, and 4h EMA fast > slow
- Exit: pred < **-0.5%**, trailing after +1.5%, ROI, -6% stop
- Risk: protections on strategy; whitelist BTC/XRP/SOL only
- Alt (not active): `FreqaiSpotClassifierStrategy` + `LightGBMClassifier`
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
        FreqaiSpotStrategy.py            # active FreqAI brain (regression v2)
        FreqaiSpotClassifierStrategy.py  # clf experiment (not promoted)
        EmaRsiV2Strategy.py
        EmaRsiStrategy.py
      models/                  # trained FreqAI models (local, gitignored)
```

