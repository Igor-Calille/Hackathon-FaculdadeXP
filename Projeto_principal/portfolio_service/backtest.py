import backtrader as bt
import pandas as pd
from ml_strategy import MLStrategy


class CustomPandasData(bt.feeds.PandasData):
    # Adicionar campos personalizados (indicadores e sinais)
    lines = ('rsi_14', 'stoch_rsi_14', 'macd', 'ema_14', 'signal_ml', 'sharpe_ratio')
    # Mapeamento dos campos com as colunas do DataFrame
    params = (
        ('rsi_14', -1),
        ('stoch_rsi_14', -1),
        ('macd', -1),
        ('ema_14', -1),
        ('signal_ml', -1),
        ('sharpe_ratio', -1),
    )


def load_data(stock, file_path):
    df = pd.read_csv(file_path, parse_dates=['date'])
    df.set_index('date', inplace=True)
    return df

def run_backtest(tickers, valor_inicial=10000):
    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(valor_inicial)  # Usar o valor inicial passado na requisição

    # Adicionar os dados das ações ao backtrader
    for stock in tickers:
        data = CustomPandasData(
            dataname=load_data(stock, f'csv_data/{stock}_data_with_sharpe.csv'),
            datetime=None,
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=-1,
            rsi_14='rsi_14',
            stoch_rsi_14='stoch_rsi_14',
            macd='macd',
            ema_14='ema_14',
            signal_ml='signal_ml',
            sharpe_ratio='sharpe_ratio',
        )
        cerebro.adddata(data, name=stock)

    # Adicionar a estratégia
    cerebro.addstrategy(MLStrategy)

    # Executar o backtest
    strategies = cerebro.run()

    # Capturar a primeira estratégia executada
    strat = strategies[0]

    # Obter o valor do portfólio e retornar
    results = [{'date': entry['date'], 'total_portfolio_value': entry['total_portfolio_value']} for entry in strat.value_list]
    for entry in strat.value_list:
        for stock in tickers:
            entry[stock] = entry.get(stock, 0)

    return results

