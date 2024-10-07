import backtrader as bt
import pandas as pd
from datetime import datetime
from yfinance_data import YFinanceData
from indicadores import Indicadores
from backtest import Test
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV


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


# Classe customizada para adicionar novos campos de dados no backtrader
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


class MLStrategy(bt.Strategy):
    params = (
        ('start_date', datetime(2021, 1, 1)),  # Data de início
        ('risk_per_trade', 1.0),               # Risco por trade
        ('initial_cash', 10000),               # Valor inicial do portfólio
    )

    def __init__(self):
        self.data_start = self.p.start_date
        self.allocation = {}  # Para manter a alocação inicial
        self.initialized = False
        self.value_list = []  # Lista para armazenar o valor do portfólio a cada dia

    def next(self):
        # Verificar se já atingimos a data de início
        if self.data.datetime.date(0) < self.data_start.date():
            return

        # Inicializar a alocação apenas uma vez (baseado no Sharpe Ratio inicial)
        if not self.initialized:
            self.allocate_portfolio()
            self.initialized = True

        # Seguir o sinal de machine learning para compra ou venda
        for d in self.datas:
            if self.getposition(d).size == 0:
                if d.signal_ml[0] == 1:  # Sinal de compra
                    size = self.calculate_position_size(d)
                    self.buy(data=d, size=size)
            elif d.signal_ml[0] == -1:  # Sinal de venda
                self.sell(data=d, size=self.getposition(d).size)

        # Armazenar o valor do portfólio ao final de cada dia, incluindo o valor alocado em cada ativo
        day_value = {'date': self.data.datetime.date(0), 'total_portfolio_value': self.broker.get_value()}
        for d in self.datas:
            position_value = self.getposition(d).size * d.close[0]  # Valor alocado na ação
            day_value[d._name] = position_value

        self.value_list.append(day_value)

    def allocate_portfolio(self):
        # Calcular o Sharpe Ratio total e as alocações para cada ativo
        total_sharpe = sum([d.sharpe_ratio[0] for d in self.datas if len(d.sharpe_ratio)])
        for d in self.datas:
            sharpe = d.sharpe_ratio[0]
            allocation_percent = (sharpe / total_sharpe) * self.p.initial_cash if total_sharpe != 0 else 0
            self.allocation[d._name] = allocation_percent
            # Comprar a alocação inicial para cada ativo
            size = allocation_percent // d.close[0]
            self.buy(data=d, size=size)

    def calculate_position_size(self, data):
        # O tamanho da posição será baseado no dinheiro disponível para aquele ativo
        cash_available = self.broker.get_cash()  # Pega o valor em caixa restante
        size = cash_available // data.close[0]  # Calcula o número de ações que pode comprar
        return size

    def stop(self):
        # Quando a estratégia terminar, salvar os valores do portfólio e as alocações em um CSV
        df = pd.DataFrame(self.value_list)
        df.to_csv('portfolio_values_and_allocations.csv', index=False)


# Função para carregar dados do CSV
def load_data(stock, file_path):
    df = pd.read_csv(file_path, parse_dates=['date'])
    df.set_index('date', inplace=True)
    df['signal_ml'] = df['signal_ml'].fillna(0)
    return df


def main(stocks_list):
    start_date = '2021-01-01'
    yfi = YFinanceData()
    yf_data = yfi.get_data_from_date(list_tickers=stocks_list, start_date=start_date)

    accuracy = {}
    best_params = {}
    signals = {}
    sharpe_ratios = {}

    federal_fund_rate = pd.read_csv('DFF.csv')
    federal_fund_rate['DATE'] = pd.to_datetime(federal_fund_rate['DATE'], errors='coerce')
    federal_fund_rate.set_index('DATE', inplace=True)

    for idx, (key, value) in enumerate(yf_data.items()):
        value['target'] = value['close'].shift(-1)
        features = ['open', 'high', 'low', 'close', 'volume']

        ind = Indicadores()
        value['rsi_14'] = ind.get_rsi(value['close'])
        features.append('rsi_14')
        value['stoch_rsi_14'] = ind.get_stochastic_rsi(value['close'])
        features.append('stoch_rsi_14')
        value['macd'] = ind.get_macd(value['close'])
        features.append('macd')
        value['ema_14'] = ind.get_media_movel_exponecial(value['close'])
        features.append('ema_14')

        value.dropna(inplace=True)

        X = value[features]
        y = value['target']

        tscv = TimeSeriesSplit(n_splits=5)
        model = RandomForestRegressor(random_state=42)

        param_search = {
            'n_estimators': [50, 100],
            'max_features': ['sqrt', 'log2'],
            'max_depth': [None, 10],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2],
            'bootstrap': [True, False]
        }

        gsearch = GridSearchCV(estimator=model, cv=tscv, param_grid=param_search, scoring='neg_mean_squared_error', n_jobs=-1, verbose=2)
        gsearch.fit(X, y)
        best_model = gsearch.best_estimator_

        best_params[key] = gsearch.best_params_

        value['predicted_price'] = best_model.predict(X)
        value['signal_ml'] = np.where(value['predicted_price'] > value['close'], 1, -1)

        value['sharpe_ratio'] = calculate_sharpe_ratio(value, federal_fund_rate, frequency='daily')
        sharpe_ratios[key] = value['sharpe_ratio']

        value.to_csv(f'csv_data/{key}_data_with_sharpe.csv', index=False)

    # Backtrader setup
    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(10000)

    for stock in stocks_list:
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

    cerebro.addstrategy(MLStrategy)
    cerebro.run()

if __name__ == '__main__':
    stocks_list = ['AAPL', 'MSFT']
    main(stocks_list)

