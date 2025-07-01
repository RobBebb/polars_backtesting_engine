from datetime import datetime

import polars as pl
from securities_load.securities.polar_table_functions import retrieve_ohlcv_using_dates


class DataHandler:
    """Data handler class for loading and processing data."""

    def __init__(
        self,
        exchange_code: str,
        ticker: str,
        start: datetime,
        end: datetime,
    ):
        """Initialize the data handler."""
        self.exchange_code = exchange_code.upper()
        self.ticker = ticker.upper()
        self.start = start
        self.end = end

    def load_data_from_local_database(self) -> pl.DataFrame:
        """Load data from a local database."""

        start_string_date = datetime.strftime(self.start, "%Y-%m-%d")
        end_string_date = datetime.strftime(self.end, "%Y-%m-%d")

        return retrieve_ohlcv_using_dates(
            exchange_code=self.exchange_code,
            ticker=self.ticker,
            start_date=start_string_date,
            end_date=end_string_date,
        )
