import yfinance as yf
import pandas as pd


class YFinanceData():
    def __init__(self) -> None:
        pass

    def get_data_from_date(self, list_tickers:str, start_date:str):
        data_dict = {}

        for symbol in list_tickers:
            stock_data = yf.download(symbol, start=start_date)
            data_dict[symbol] = stock_data


        return data_dict
    

