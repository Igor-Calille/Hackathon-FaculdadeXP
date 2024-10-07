import yfinance as yf
import pandas as pd

class YFinanceData:
    def __init__(self):
        pass

    def get_data_from_date(self, list_tickers, start_date):
        stock_data = {}

        for ticker in list_tickers:
            stock_data[ticker] = yf.download(ticker, start=start_date)
            

            stock_data[ticker].reset_index(inplace=True)

            stock_data[ticker] = stock_data[ticker][['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            stock_data[ticker].columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        return stock_data
