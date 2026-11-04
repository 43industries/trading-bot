# Trading Bot (Freqtrade)

Crypto spot bot built on [Freqtrade](https://github.com/freqtrade/freqtrade) + CCXT.

**Defaults:** Binance spot · `XRP/USDT` + `SOL/USDT` · `1h` · **dry-run** · strategy `EmaRsiV2Strategy`

This repo does **not** guarantee profit. You must pass the gates below before live trading.

## Setup

```powershell
cd freqtrade
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip wheel
python -m pip install -e .
freqtrade install-ui
Copy-Item user_data\config.example.json user_data\config.json
# Edit user_data\config.json (API password, optional exchange keys)
freqtrade --version
```

## Commands

### Download history

```powershell
freqtrade download-data --config user_data/config.json --exchange binance --pairs XRP/USDT SOL/USDT --timeframes 1h 4h --timerange 20250101- --userdir user_data
```

### Backtest

```powershell
freqtrade backtesting --config user_data/config.json --strategy EmaRsiV2Strategy --userdir user_data --timerange 20250101-
```

### Dry-run (paper trade)

```powershell
freqtrade trade --config user_data/config.json --strategy EmaRsiV2Strategy --userdir user_data
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

### Latest backtest (`EmaRsiV2Strategy`, XRP+SOL 1h+4h filter, 2025-01 → 2025-11)

| Metric | V2 result | V1 (for compare) | Gate |
|--------|-----------|------------------|------|
| Trades | 10 (SOL 8 / XRP 2) | 177 | **Fail** (sample thin) |
| Total profit | **-0.41%** (-4.1 USDT) | -3.94% | **Fail** (expectancy) |
| Profit factor | 0.59 | 0.73 | **Fail** (< 1) |
| Max drawdown | 0.55% | 4.29% | Pass (≤ 20%) |
| Per pair | XRP **+0.35%** · SOL -0.76% | SOL -0.71% · XRP -3.23% | — |
| Exit notes | exit_signal still 5 losers; ROI/trail profitable | exit_signal dominated losses | — |

**Verdict: do not go live.** V2 lost less than V1 and XRP turned slightly positive, but expectancy and sample size still fail. Next: hyperopt EMA/RSI/trail params, or refine exits further.

### Brain V2 rules (active)

- Entry: 4h EMA uptrend + 1h EMA cross up + RSI 40–55 + volume > SMA20
- Exit: 1h EMA cross down only (no RSI exit) + trailing stop (+1.5% offset, 1% trail) + ROI + -6% stop
- Baseline V1 kept at `EmaRsiStrategy.py`

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
        EmaRsiStrategy.py      # V1 baseline
        EmaRsiV2Strategy.py    # active brain
```
