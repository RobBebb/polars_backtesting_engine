"""Performance module for calculating performance metrics."""

import numpy as np
import polars as pl


def calculate_exposure(stock: pl.Series, total_aum: pl.Series) -> float:
    """Calculate the exposure of a stock in the portfolio."""
    exposure = (stock / total_aum).mean()
    return pl.select(exposure).item()


def calculate_total_return(
    final_portfolio_value: float, initial_capital: float
) -> float:
    """Calculate the total return of the portfolio as a fraction.
    Multiply by 100 to get a percentage return."""
    return (final_portfolio_value / initial_capital) - 1


def calculate_annualized_return(
    total_return: float, days_invested: int, days_in_year: int
) -> float:
    """Calculate the annualized return of the portfolio."""
    return np.power((1 + total_return), 1 / (days_invested / days_in_year)) - 1


def calculate_annualized_volatility(
    daily_returns: pl.Series, trading_days: int = 252
) -> float:
    """Calculate the annualized volatility of the portfolio."""
    return daily_returns.std() * np.sqrt(trading_days)


def calculate_sharpe_ratio(
    annualized_return: float, annualized_volatility: float, risk_free_rate: float = 0.0
) -> float:
    """Calculate the Sharpe ratio of the portfolio."""
    try:
        return (annualized_return - risk_free_rate) / annualized_volatility
    except RuntimeError:
        return np.nan


def calculate_sortino_ratio(
    daily_returns: pl.Series, annualized_return: float, risk_free_rate: float = 0.0
) -> float:
    """Calculate the Sortino ratio of the portfolio."""
    negative_returns = daily_returns.filter(daily_returns < 0)
    downside_volatility = negative_returns.std() * np.sqrt(252)
    return (
        (annualized_return - risk_free_rate) / downside_volatility
        if downside_volatility > 0
        else np.nan
    )


def calculate_maximum_drawdown(portfolio_values: pl.Series) -> float:
    """Calculate the maximum drawdown of the portfolio."""
    drawdown = portfolio_values / portfolio_values.cum_max() - 1

    return pl.select(drawdown.min()).item()
