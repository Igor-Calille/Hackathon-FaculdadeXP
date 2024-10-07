import yfinance as yf
import pandas as pd

class YFinanceData:
    def __init__(self) -> None:
        pass

    def get_data_from_date(self, list_tickers: str, start_date: str):
        data_dict = {}

        for symbol in list_tickers:
            stock_data = yf.download(symbol, start=start_date)
            stock_data.reset_index(inplace=True)
            stock_data = stock_data.rename(columns={
                'Date': 'date', 'Open': 'open', 'High': 'high', 
                'Low': 'low', 'Close': 'close', 'Volume': 'volume', 
                'Adj Close': 'adj_close'
            })
            data_dict[symbol] = stock_data

        return data_dict
