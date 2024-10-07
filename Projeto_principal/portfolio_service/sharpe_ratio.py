import pandas as pd

def calculate_sharpe_ratio(stock_data, risk_free_rate, frequency='daily'):
    stock_data.index = pd.to_datetime(stock_data.index, errors='coerce')
    risk_free_rate.index = pd.to_datetime(risk_free_rate.index, errors='coerce')
    stock_data.dropna(subset=['close'], inplace=True)
    risk_free_rate.dropna(inplace=True)

    if frequency == 'daily':
        stock_data['returns'] = stock_data['close'].pct_change()
        risk_free_rate = risk_free_rate.resample('D').ffill()
    elif frequency == 'monthly':
        stock_data['returns'] = stock_data['close'].resample('M').ffill().pct_change()
        risk_free_rate = risk_free_rate.resample('M').ffill()

    stock_data, risk_free_rate = stock_data.align(risk_free_rate, join='inner', axis=0)
    excess_returns = stock_data['returns'] - risk_free_rate['DFF']
    stock_data['sharpe_ratio'] = excess_returns / excess_returns.rolling(window=370).std()

    return stock_data['sharpe_ratio']
