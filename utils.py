from enum import Enum, unique


@unique
class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


@unique
class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
