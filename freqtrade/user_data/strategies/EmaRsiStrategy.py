# pragma pylint: disable=missing-docstring, invalid-name
# --- Do not remove these imports ---
from pandas import DataFrame

from freqtrade.strategy import IStrategy, IntParameter

import talib.abstract as ta
from technical import qtpylib


class EmaRsiStrategy(IStrategy):
    """
    Spot long-only strategy: EMA fast/slow crossover filtered by RSI.

    Entry: EMA fast crosses above EMA slow AND RSI is between oversold and mid.
    Exit:  EMA fast crosses below EMA slow OR RSI is overbought.
    """

    INTERFACE_VERSION = 3
    can_short: bool = False

    # Take profit ladder (overridden if config sets minimal_roi)
    minimal_roi = {
        "120": 0.01,
        "60": 0.02,
        "0": 0.04,
    }

    stoploss = -0.05
    trailing_stop = False

    timeframe = "1h"
    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Warmup for the slower EMA
    startup_candle_count: int = 60

    # Hyperoptable / tunable parameters
    ema_fast = IntParameter(5, 20, default=12, space="buy", optimize=True)
    ema_slow = IntParameter(21, 60, default=26, space="buy", optimize=True)
    rsi_period = IntParameter(10, 20, default=14, space="buy", optimize=True)
    rsi_entry_min = IntParameter(30, 45, default=35, space="buy", optimize=True)
    rsi_entry_max = IntParameter(50, 65, default=60, space="buy", optimize=True)
    rsi_exit = IntParameter(65, 85, default=70, space="sell", optimize=True)

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
        },
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=int(self.ema_fast.value))
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=int(self.ema_slow.value))
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=int(self.rsi_period.value))
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe["ema_fast"], dataframe["ema_slow"])
                & (dataframe["rsi"] > self.rsi_entry_min.value)
                & (dataframe["rsi"] < self.rsi_entry_max.value)
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (
                    qtpylib.crossed_below(dataframe["ema_fast"], dataframe["ema_slow"])
                    | (dataframe["rsi"] > self.rsi_exit.value)
                )
                & (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe
