from polars_backtesting_engine.utils import OrderSide, OrderType


class Order:
    """When buying or selling, we first create an order object. If the order is filled, we create a trade object."""

    def __init__(
        self,
        ticker: str,
        side: OrderSide,
        size: float,
        idx: int,
        limit_price: float | None = None,
        order_type: OrderType = OrderType.MARKET,
    ):
        self.ticker = ticker
        self.side = side
        self.size = size
        self.type = order_type
        self.limit_price = limit_price
        self.idx = idx
