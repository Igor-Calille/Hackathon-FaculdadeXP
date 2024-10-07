import pandas as pd
import backtrader as bt
import pandas as pd
from datetime import datetime
from yfinance_data import YFinanceData
from indicadores import Indicadores
from backtest import Test
def calculate_buy_and_hold(stock_data, initial_cash):
    # Preço inicial (primeiro preço de fechamento)
    initial_price = stock_data['close'].iloc[0]

    # Quantidade de ações compradas no início
    num_shares = initial_cash // initial_price

    # Valor do portfólio em cada dia (número de ações vezes o preço de fechamento)
    stock_data['buy_and_hold_value'] = num_shares * stock_data['close']

    # Resetar o índice para garantir que a data seja uma coluna normal no CSV
    stock_data.reset_index(inplace=True)

    return stock_data[['date', 'close', 'buy_and_hold_value']]

def main_buy_and_hold(stocks_list, initial_cash=10000):
    yfi = YFinanceData()
    start_date = '2021-01-01'
    
    # Obter os dados de cada ação
    yf_data = yfi.get_data_from_date(list_tickers=stocks_list, start_date=start_date)

    # Dicionário para armazenar os resultados de buy and hold para cada ação
    buy_and_hold_results = {}

    for stock, data in yf_data.items():
        # Calcular o buy and hold para cada ação
        buy_and_hold_data = calculate_buy_and_hold(data, initial_cash)
        
        # Salvar os resultados para cada ação em um CSV, incluindo a coluna de data
        buy_and_hold_data.to_csv(f'buy_and_hold_{stock}.csv', index=False)

        # Adicionar ao dicionário para referência futura
        buy_and_hold_results[stock] = buy_and_hold_data

    print("Buy and Hold CSV files created for each stock.")

if __name__ == '__main__':
    stocks_list = ['AAPL', 'MSFT']
    main_buy_and_hold(stocks_list)
