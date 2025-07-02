from datetime import datetime
from typing import Optional

from polars_backtesting_engine.utils import OrderSide, OrderType, PositionType


class Position:
    """Represents positions in the market"""

    def __init__(
        self,
        ticker: str,
        idx: int,
        position_type: PositionType,
        open_price: float,
        open_datetime: datetime,
        size: float,
        stop_loss: Optional[float | None],
        take_profit: Optional[float | None],
    ):
        """Initialises a new position

        Parameters
        ----------
        ticker : str
            The symbol.
        idx : int
            The index of the row on which the position was taken.
        position_type : PositionType
            Long or Short.
        open_price : float
            The price at which the position was opened.
        open_datetime : datetime
            The datetime when the positipon was opened.
        size : float
            The number of shares / contracts the position has.
        stop_loss : Optional[float  |  None]
            A price at which the position will be liquidated to limit losses.
        take_profit : Optional[float  |  None]
            A price at which the position will be liquidated to take the profit.
        """
        self.__ticker = ticker
        self.__idx = idx
        self.__position_type = position_type
        self.__open_price = open_price
        self.__open_datetime = open_datetime
        self.__size = size
        self.__stop_loss = stop_loss
        self.__take_profit = take_profit

    @property
    def ticker(self) -> str:
        """The ticker of the position"""
        return self.__ticker

    @property
    def position_type(self) -> PositionType:
        """The type of the position"""
        return self.__position_type

    @property
    def open_price(self) -> float:
        """The price at which the position was opened"""
        return self.__open_price

    @property
    def open_datetime(self) -> datetime:
        """The datetime when the position was opened"""
        return self.__open_datetime

    @property
    def size(self) -> float:
        """The number of shares / contracts the position has"""
        return self.__size

    @property
    def stop_loss(self) -> Optional[float | None]:
        """A price at which the position will be liquidated to limit losses"""
        return self.__stop_loss

    @property
    def take_profit(self) -> Optional[float | None]:
        """A price at which the position will be liquidated to take the profit"""
        return self.__take_profit

    def update_stop_loss(self, stop_loss: Optional[float | None]) -> None:
        """Updates the stop loss price.

        Args:
            stop_loss (Optional[float]): The new stop loss price. None to remove the stop loss.
        """

        self.__validate_stop_loss(stop_loss)
        self.__stop_loss = stop_loss

    def update_take_profit(self, take_profit: Optional[float | None]) -> None:
        """Updates the take profit price.

        Args:
            take_profit (Optional[float]): The new take profit price. None to remove the take profit.
        """

        self.__validate_take_profit(take_profit)
        self.__take_profit = take_profit

    def calc_value(self, current_price: float) -> float:
        """Calculates the current value of the position.

        Args:
            current_price (float): The current price of the asset.

        Returns:
            float: The current value of the position.
        """

        value = 0.0
        if self.__position_type == PositionType.LONG:
            value = current_price * self.__size
        elif self.__position_type == PositionType.SHORT:
            # TOFIX: Why is this formula used?
            value = (2 * self.__open_price - current_price) * self.__size

        return value

    def replace(self, **kwargs) -> "Position":
        """Replaces the specified properties of the position.

        Args:
            **kwargs: Optional parameters to update the position attributes. If not provided, the current values are used.

        Returns:
            Position: A new Position object with updated attributes.
        """
        return Position(
            ticker=kwargs.get("ticker", self.__ticker),
            idx=kwargs.get("idx", self.__idx),
            position_type=kwargs.get("position_type", self.__position_type),
            open_price=kwargs.get("open_price", self.__open_price),
            open_datetime=kwargs.get("open_datetime", self.__open_datetime),
            size=kwargs.get("size", self.__size),
            stop_loss=kwargs.get("stop_loss", self.__stop_loss),
            take_profit=kwargs.get("take_profit", self.__take_profit),
        )

    def __validate_stop_loss(self, stop_loss: Optional[float]) -> None:
        """Checks the stop_loss specified is valid based on the position type.

        Args:
            stop_loss (Optional[float]): The stop loss price.

        Returns:
            None
        """
        if stop_loss is None:
            return

        if self.__position_type == PositionType.LONG:
            if stop_loss > self.__open_price:
                raise ValueError(
                    "Stop loss must be lower than open price for long position"
                )
        elif self.__position_type == PositionType.SHORT:
            if stop_loss < self.__open_price:
                raise ValueError(
                    "Stop loss must be higher than open price for short position"
                )

    def __validate_take_profit(self, take_profit: Optional[float]) -> None:
        """Checks the take_profit specified is valid based on the position type.

        Args:
            take_profit (float): The take_profit price.

        Returns:
            None
        """
        if take_profit is None:
            return

        if self.__position_type == PositionType.LONG:
            if take_profit < self.__open_price:
                raise ValueError(
                    "Take profit must be higher than open price for long position"
                )
        elif self.__position_type == PositionType.SHORT:
            if take_profit > self.__open_price:
                raise ValueError(
                    "Take profit must be lower than open price for short position"
                )
