from typing import Optional

import polars as pl

from polars_backtesting_engine.order import Order
from polars_backtesting_engine.utils import OrderSide, OrderType


class Strategy:
    """This base class will handle the execution logic of our trading strategies"""

    def __init__(self):
        self.current_idx: Optional[int] = None
        self.data: Optional[pl.DataFrame] = None
        self.cash: Optional[float] = None
        self.orders: list = []
        self.trades: list = []

    def buy(self, ticker: str, size: float = 1.0) -> None:
        if self.current_idx is None:
            raise ValueError("No current_idx has been added to the strategy for buy.")
        self.orders.append(
            Order(ticker=ticker, side=OrderSide.BUY, size=size, idx=self.current_idx)
        )

    def sell(self, ticker: str, size: float) -> None:
        if self.current_idx is None:
            raise ValueError("No current_idx has been added to the strategy for sell.")
        self.orders.append(
            Order(ticker=ticker, side=OrderSide.SELL, size=-size, idx=self.current_idx)
        )

    def buy_limit(self, ticker: str, limit_price: float, size: float) -> None:
        if self.current_idx is None:
            raise ValueError("No current_idx has been added to the strategy for sell.")
        self.orders.append(
            Order(
                ticker=ticker,
                side=OrderSide.BUY,
                size=size,
                limit_price=limit_price,
                order_type=OrderType.LIMIT,
                idx=self.current_idx,
            )
        )

    def sell_limit(self, ticker: str, limit_price: float, size: float) -> None:
        if self.current_idx is None:
            raise ValueError("No current_idx has been added to the strategy for sell.")
        self.orders.append(
            Order(
                ticker=ticker,
                side=OrderSide.SELL,
                size=-size,
                limit_price=limit_price,
                order_type=OrderType.LIMIT,
                idx=self.current_idx,
            )
        )

    @property
    def position_size(self) -> float:
        return sum([t.size for t in self.trades])

    @property
    def close(self) -> float:
        if self.data is None:
            raise ValueError("No data has been added to the engine for close.")
        return self.data.filter(pl.col("date") == self.current_idx)["close"].item()

    def on_bar(self):
        """This method will be overriden by our strategies."""
        pass
