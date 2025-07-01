from typing import Optional

import altair as alt

# Import matplotlib
import matplotlib.pyplot as plt
import polars as pl

# Setting a nice style for the plots
import seaborn as sns
from tqdm import tqdm

from polars_backtesting_engine.performance import (
    calculate_annualized_return,
    calculate_annualized_volatility,
    calculate_exposure,
    calculate_maximum_drawdown,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_total_return,
)
from polars_backtesting_engine.strategy import Strategy
from polars_backtesting_engine.trade import Trade
from polars_backtesting_engine.utils import OrderSide, OrderType

sns.set_style("darkgrid")
# Make plots bigger
plt.rcParams["figure.figsize"] = [10, 6]


class Engine:
    """The engine is the main object that will be used to run our backtest."""

    def __init__(self, initial_cash: float = 100000.00):
        self.strategy: Optional[Strategy] = None
        self.cash: float = initial_cash
        self.initial_cash: float = initial_cash
        self.data: Optional[pl.DataFrame] = None
        self.current_idx = None
        self.cash_series: dict = {}
        self.stock_series: dict = {}
        # I’m assuming we’re using daily data of an asset that trades only
        # during working days (i.e., stocks). If you’re trading cryptocurrencies,
        # use 365 instead of 252 for trading_days
        self.trading_days: int = 252
        self.days_in_year: int = 365
        # For simplicity, I’m assuming a risk-free rate of 0
        self.risk_free_rate: float = 0

    def add_data(self, data: pl.DataFrame):
        # Add OHLC data to the engine
        self.data = data

    def add_strategy(self, strategy: Strategy):
        # Add a strategy to the engine
        self.strategy = strategy

    def run(self):
        if self.strategy is None:
            raise ValueError("No strategy has been added to the engine.")
        if self.data is None:
            raise ValueError("No data has been added to the engine.")
        # We need to preprocess a few things before running the backtest
        self.strategy.data = self.data
        self.strategy.cash = self.cash

        # idx is a tuple of (date, open, high, low, close, volume)
        for idx in tqdm(self.data.iter_rows()):
            self.current_idx = idx[0]
            self.strategy.current_idx = self.current_idx
            # fill orders from previus period
            self._fill_orders()

            # Run the strategy on the current bar
            self.strategy.on_bar()
            self.cash_series[self.current_idx] = self.cash
            self.stock_series[self.current_idx] = self.strategy.position_size * idx[4]
        return self._get_stats()

    def _fill_orders(self):
        """this method fills buy and sell orders, creating new trade objects and adjusting the strategy's cash balance.
        Conditions for filling an order:
        - If we're buying, our cash balance has to be large enough to cover the order.
        - If we are selling, we have to have enough shares to cover the order.

        """
        if self.strategy is None:
            raise ValueError(
                "No strategy has been added to the engine for _fill_orders."
            )
        if self.data is None:
            raise ValueError("No data has been added to the engine for _fill_orders.")
        if self.current_idx is None:
            raise ValueError(
                "No current_idx has been added to the engine for _fill_orders."
            )
        for order in self.strategy.orders:
            # FOR NOW, SET FILL PRICE TO EQUAL OPEN PRICE. THIS HOLDS TRUE FOR MARKET ORDERS
            fill_price = self.data.filter(pl.col("date") == self.current_idx)[
                "open"
            ].item()
            can_fill = False
            if fill_price is None:
                raise ValueError(
                    f"Open price is None for {self.current_idx} in _fill_orders."
                )
            if order.side == OrderSide.BUY and self.cash >= order.size * fill_price:
                if order.type == OrderType.LIMIT:
                    # LIMIT BUY ORDERS ONLY GET FILLED IF THE LIMIT PRICE IS GREATER THAN OR EQUAL TO THE LOW PRICE
                    # TODO: WHAT HAPPENS IF THE LIMIT PRICE IS GREATER THAN THE OPEN, WILL WE HAVE ENOUGH MONEY?
                    # If limit price is greater than open will fill at limit price so may not have enough money
                    # to cover the order.
                    low_price = self.data.filter(pl.col("date") == self.current_idx)[
                        "low"
                    ].item()
                    if order.limit_price >= low_price:
                        fill_price = order.limit_price
                        can_fill = True
                        print(
                            self.current_idx,
                            "Buy Filled. ",
                            "limit",
                            order.limit_price,
                            " / low",
                            low_price,
                        )

                    else:
                        print(
                            self.current_idx,
                            "Buy NOT filled. ",
                            "limit",
                            order.limit_price,
                            " / low",
                            low_price,
                        )
                else:
                    can_fill = True
            elif (
                order.side == OrderSide.SELL
                and self.strategy.position_size >= order.size
            ):
                if order.type == OrderType.LIMIT:
                    # LIMIT SELL ORDERS ONLY GET FILLED IF THE LIMIT PRICE IS LESS THAN OR EQUAL TO THE HIGH PRICE
                    high_price = self.data.filter(pl.col("date") == self.current_idx)[
                        "high"
                    ].item()
                    if order.limit_price <= high_price:
                        fill_price = order.limit_price
                        can_fill = True
                        print(
                            self.current_idx,
                            "Sell filled. ",
                            "limit",
                            order.limit_price,
                            " / high",
                            high_price,
                        )
                    else:
                        print(
                            self.current_idx,
                            "Sell NOT filled. ",
                            "limit",
                            order.limit_price,
                            " / high",
                            high_price,
                        )
                else:
                    can_fill = True

            if can_fill:
                t = Trade(
                    ticker=order.ticker,
                    side=order.side,
                    size=order.size,
                    price=fill_price,
                    type=order.type,
                    idx=self.current_idx,
                )

                self.strategy.trades.append(t)
                self.cash -= t.price * t.size
                self.strategy.cash = self.cash

        # By clearing the list of pending orders at the end of the method,
        # we are assuming that limit orders are only valid for the day.
        # This behavior tends to be the default. Implementing good till-granted (GTC)
        # orders would require us to keep all unfilled limit orders.
        self.strategy.orders = []

    def _get_stats(self) -> dict:
        if self.strategy is None:
            raise ValueError("No strategy has been added to the engine for _get_stats.")
        if self.data is None:
            raise ValueError("No data has been added to the engine for _get_stats.")
        if self.stock_series is None:
            raise ValueError(
                "No stock_series has been added to the engine for _get_stats."
            )
        portfolio = pl.DataFrame(
            {
                "keys": list(self.stock_series.keys()),
                "stock": list(self.stock_series.values()),
                "cash": list(self.cash_series.values()),
            },
            strict=False,
        )
        portfolio = portfolio.with_columns(total_aum=pl.col("stock") + pl.col("cash"))

        # Create a dataframe with the cash and stock holdings at the end of each bar
        # portfolio = pl.DataFrame({"stock": self.stock_series, "cash": self.cash_series})
        # Add a third column with the total assets under managemet
        # portfolio["total_aum"] = portfolio["stock"] + portfolio["cash"]
        # Caclulate the total exposure to the asset as a percentage of our total holdings

        self.portfolio = portfolio

        p = portfolio["total_aum"]
        metrics = {}

        calc_exposure = calculate_exposure(self.portfolio["stock"], p)
        metrics["exposure"] = round(calc_exposure, 7)

        calc_total_return = calculate_total_return(p[-1], p[0])
        metrics["total_return"] = round(calc_total_return, 7)

        # days_invested = portfolio[0, 0] - portfolio[-1, 0].days()
        days_invested = (portfolio["keys"].max() - portfolio["keys"].min()).days  # type: ignore
        calc_annualised_return = calculate_annualized_return(
            calc_total_return, days_invested, self.days_in_year
        )
        metrics["annualised_return"] = round(calc_annualised_return, 7)

        daily_returns = p.pct_change()
        calc_annualised_volatility = calculate_annualized_volatility(
            daily_returns, self.trading_days
        )
        metrics["annualised_volatility"] = round(calc_annualised_volatility, 7)

        calc_sharpe_ratio = calculate_sharpe_ratio(
            calc_annualised_return, calc_annualised_volatility, self.risk_free_rate
        )
        metrics["sharpe_ratio"] = round(calc_sharpe_ratio, 7)

        calc_sortino_ratio = calculate_sortino_ratio(
            daily_returns, calc_annualised_return, self.risk_free_rate
        )
        metrics["sortino_ratio"] = round(calc_sortino_ratio, 7)

        calc_maximum_drawdown = calculate_maximum_drawdown(portfolio["total_aum"])
        metrics["max_drawdown"] = round(calc_maximum_drawdown, 7)

        # Buy & Hold Benchmark
        portfolio_bh = self.initial_cash / self.data[0, "open"] * self.data[:, "close"]
        self.portfolio_bh = portfolio_bh
        p_bh = portfolio_bh

        calc_bh_total_return = calculate_total_return(p_bh[-1], p_bh[0])
        metrics["bh_total_return"] = round(calc_bh_total_return, 7)

        bh_days_invested = (self.data["date"].max() - self.data["date"].min()).days  # type: ignore
        calc_bh_annualised_return = calculate_annualized_return(
            calc_bh_total_return, bh_days_invested, self.days_in_year
        )
        metrics["bh_annualised_return"] = round(calc_bh_annualised_return, 7)

        bh_daily_returns = p_bh.pct_change()
        calc_bh_annualised_volatility = calculate_annualized_volatility(
            bh_daily_returns, self.trading_days
        )
        metrics["bh_annualised_volatility"] = round(calc_bh_annualised_volatility, 7)

        calc_bh_sharpe_ratio = calculate_sharpe_ratio(
            calc_bh_annualised_return,
            calc_bh_annualised_volatility,
            self.risk_free_rate,
        )
        metrics["bh_sharpe_ratio"] = round(calc_bh_sharpe_ratio, 7)

        calc_sortino_ratio = calculate_sortino_ratio(
            bh_daily_returns, calc_bh_annualised_return, self.risk_free_rate
        )
        metrics["bh_sortino_ratio"] = round(calc_sortino_ratio, 7)

        calc_bh_maximum_drawdown = calculate_maximum_drawdown(portfolio_bh)
        metrics["bh_max_drawdown"] = round(calc_bh_maximum_drawdown, 7)

        return metrics

    def plot(self):
        alt.renderers.enable("mimetype")
        # alt.renderers.enable("jupyter")
        # self.portfolio = self.portfolio.unstack()
        # self.portfolio.unstack(level=0).plot(kind="line", subplots=True)
        data = self.portfolio
        stock = (
            alt.Chart(data)
            .mark_line()
            .encode(alt.X("keys", title=""), alt.Y("stock", title=("Stock")))
            .properties(height=50, title="Assets Under Management")
        )

        cash = stock.encode(
            alt.X("keys", title=""), alt.Y("cash", title=("Cash"))
        ).properties(height=50, title="")

        total_aum = stock.encode(
            alt.X("keys", title=("Date")),
            alt.Y("total_aum").title("Total Assets").scale(zero=False),
        ).properties(height=100, title="")

        chart = alt.vconcat(stock, cash, total_aum)
        chart.save("chart.html")
