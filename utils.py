from enum import Enum, unique


@unique
class OrderSide(Enum):
    BUY = "buy"  # Purchase an asset - this could open a long position or close a short one.
    SELL = (
        "sell"  # Sell an asset - this could open a short position or close a long one.
    )


@unique
class OrderType(Enum):
    MARKET = "market"  # Instruction to buy or sell a stock immediately at the best available price
    LIMIT = "limit"  # Instruction to buy or sell a stock at a specified price or better (the limit price or lower for a buy and the limit price or higher for a sell)
    STOP = "stop"  # An instruction to buy or sell a stock once it reaches a specified price, known as the "stop price". When the stock price hits the "stop price" the stop order becomes a market order.
    STOP_LIMIT = "stop_limit"  # An instruction to buy or sell a stock once it reaches a specified price, known as the "stop price" and only while the price is at or better than the "limit price". When the stock price hits the "stop price" the stop order becomes a limit order.


@unique
class PositionType(Enum):
    LONG = "long"  # You believe the asset will go up in value, so you buy it, hoping to sell later at a higher price.
    SHORT = "short"  # You believe the asset will go down in value, so you borrow and sell it, hoping to but it back cheaper.
