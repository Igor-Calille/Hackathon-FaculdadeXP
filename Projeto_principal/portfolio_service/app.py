from flask import Flask, request, jsonify
from yfinance_data import YFinanceData
from ml_model import train_ml_model
from sharpe_ratio import calculate_sharpe_ratio
from backtest import run_backtest
import os
import pandas as pd

app = Flask(__name__)

@app.route('/portfolio/value', methods=['POST'])
def calculate_portfolio():
    data = request.json
    tickers = data.get('tickers', [])
    start_date = data.get('start_date', '2021-01-01')
    valor_inicial = data.get('valor_inicial', 10000)  # Valor inicial padrão caso não seja passado

    if not os.path.exists('csv_data'):
        os.makedirs('csv_data')

    yfi = YFinanceData()
    dados_acoes = yfi.get_data_from_date(tickers, start_date)

    # Carregar taxa de juros livre de risco
    federal_fund_rate = pd.read_csv('DFF.csv')
    federal_fund_rate['DATE'] = pd.to_datetime(federal_fund_rate['DATE'], errors='coerce')
    federal_fund_rate.set_index('DATE', inplace=True)

    resultados = {}
    for ticker, dados in dados_acoes.items():
        # Treinar o modelo de ML e calcular Sharpe Ratio
        sinais_ml = train_ml_model(dados)
        dados['signal_ml'] = sinais_ml

        # Calcular o Sharpe Ratio e adicioná-lo ao DataFrame
        sharpe = calculate_sharpe_ratio(dados, federal_fund_rate)
        dados['sharpe_ratio'] = sharpe

        dados.to_csv(f'csv_data/{ticker}_data_with_sharpe.csv', index=False)

    portfolio_values = run_backtest(tickers, valor_inicial)

    return jsonify(portfolio_values)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
