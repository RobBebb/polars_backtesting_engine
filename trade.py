from polars_backtesting_engine.utils import OrderSide, OrderType


class Trade:
    """Trade objects are created when an order is filled."""

    def __init__(
        self,
        ticker: str,
        side: OrderSide,
        size: float,
        price: float,
        type: OrderType,
        idx: int,
    ):
        self.ticker = ticker
        self.side = side
        self.size = size
        self.type = type
        self.price = price
        self.idx = idx

    # Trade class string representation dunder method
    def __repr__(self) -> str:
        return f"<Trade: {self.idx} {self.ticker} {self.side.value} {self.type.value} {self.size}@{self.price}>"
