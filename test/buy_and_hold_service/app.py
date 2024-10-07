from flask import Flask, request, jsonify
from calculo_buy_hold import calcular_buy_and_hold

app = Flask(__name__)

@app.route('/buyhold/value', methods=['POST'])
def buy_hold_value():
    data = request.json
    tickers = data.get('tickers', [])
    start_date = data.get('start_date', '2021-01-01')  # Data padrão
    valor_inicial = data.get('valor_inicial', 10000)  # Valor inicial padrão
    
    # Calcular o Buy and Hold com base no valor inicial
    result = calcular_buy_and_hold(tickers, start_date, valor_inicial)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
