# pragma pylint: disable=missing-docstring, invalid-name
from pandas import DataFrame

from freqtrade.strategy import IStrategy, IntParameter, informative

import talib.abstract as ta
from technical import qtpylib


class EmaRsiV2Strategy(IStrategy):
    """
    V2 long-only trend brain for XRP/SOL (and any spot pair).

    Entry: 4h EMA trend up + 1h EMA cross up + RSI 40-55 + volume > SMA20.
    Exit: 1h EMA cross down only (no RSI exit) + trailing stop + ROI + stoploss.
    """

    INTERFACE_VERSION = 3
    can_short: bool = False

    minimal_roi = {
        "120": 0.01,
        "60": 0.025,
        "0": 0.05,
    }

    stoploss = -0.06

    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    timeframe = "1h"
    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Enough base candles for 4h EMA26 warmup after merge
    startup_candle_count: int = 200

    ema_fast = IntParameter(5, 20, default=12, space="buy", optimize=True)
    ema_slow = IntParameter(21, 60, default=26, space="buy", optimize=True)
    rsi_period = IntParameter(10, 20, default=14, space="buy", optimize=True)
    rsi_entry_min = IntParameter(35, 45, default=40, space="buy", optimize=True)
    rsi_entry_max = IntParameter(50, 60, default=55, space="buy", optimize=True)
    volume_ma = IntParameter(10, 40, default=20, space="buy", optimize=True)

    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    plot_config = {
        "main_plot": {
            "ema_fast": {"color": "blue"},
            "ema_slow": {"color": "orange"},
        },
        "subplots": {
            "RSI": {
                "rsi": {"color": "purple"},
            },
            "Volume": {
                "volume_mean": {"color": "gray"},
            },
        },
    }

    @informative("4h")
    def populate_indicators_4h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=12)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=26)
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=int(self.ema_fast.value))
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=int(self.ema_slow.value))
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=int(self.rsi_period.value))
        dataframe["volume_mean"] = dataframe["volume"].rolling(
            int(self.volume_ma.value)
        ).mean()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["ema_fast_4h"] > dataframe["ema_slow_4h"])
                & qtpylib.crossed_above(dataframe["ema_fast"], dataframe["ema_slow"])
                & (dataframe["rsi"] > self.rsi_entry_min.value)
                & (dataframe["rsi"] < self.rsi_entry_max.value)
                & (dataframe["volume"] > dataframe["volume_mean"])
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # EMA cross down only — RSI forced exit removed in V2
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe["ema_fast"], dataframe["ema_slow"])
                & (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe
