import yfinance as yf
import pandas as pd

def calcular_buy_and_hold(tickers, start_date, valor_inicial=10000):
    resultados = {}

    for ticker in tickers:
        dados = yf.download(ticker, start=start_date)
        
        dados['portfolio_value'] = (dados['Close'] / dados['Close'].iloc[0]) * valor_inicial
        
        resultados[ticker] = dados[['Open', 'High', 'Low', 'Close', 'Adj Close', 'portfolio_value']].reset_index().to_dict(orient='records')

    return resultados
