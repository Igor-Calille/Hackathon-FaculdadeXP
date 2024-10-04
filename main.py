from yfinance_data import YFinanceData

stocks_list = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA']

yfi = YFinanceData()
yf_data = yfi.get_data_from_date(list_tickers=stocks_list, start_date='2022-01-01')

print(yf_data)