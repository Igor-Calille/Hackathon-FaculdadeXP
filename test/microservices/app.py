from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

# Função para ler o CSV
def read_csv(file_path):
    try:
        # Lê o CSV usando pandas
        df = pd.read_csv(file_path)
        # Converte o DataFrame em uma lista de dicionários
        data = df.to_dict(orient='records')
        return data
    except Exception as e:
        return str(e)

# Endpoint para retornar o conteúdo do CSV
@app.route('/read_csv', methods=['GET'])
def get_csv_data():
    file_path = 'code\\portfolio_values_and_allocations.csv'  # Caminho do arquivo CSV
    data = read_csv(file_path)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
