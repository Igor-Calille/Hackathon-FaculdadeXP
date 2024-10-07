import backtrader as bt
import pandas as pd
from datetime import datetime

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
        df = pd.DataFrame(self.value_list)
        df.to_csv('portfolio_values_and_allocations.csv', index=False)
