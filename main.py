from flask import Flask, request, jsonify
from flask_cors import CORS  # Importa o Flask-CORS para permitir requisições de qualquer origem
import bordero  # Importa o arquivo responsável pelo processamento de borderô
import cnpja    # Importa o arquivo responsável pela consulta de CNPJ
import os

app = Flask(__name__)
CORS(app)  # Habilita CORS para aceitar requisições de qualquer origem

# Rota para extrair dados de um borderô
@app.route('/extrair-bordero', methods=['POST'])
def extrair_bordero():
    data = request.json
    drive_id = data.get('drive_id')

    if not drive_id:
        return jsonify({"error": "drive_id não fornecido"}), 400

    resultado = bordero.processar_bordero(drive_id)
    return jsonify(resultado)

# Rota para consultar dados de um CNPJ (GET)
@app.route('/consulta-cnpj/<cnpj>', methods=['GET'])
def consulta_cnpj(cnpj):
    if not cnpj:
        return jsonify({"error": "CNPJ não fornecido"}), 400

    resultado = cnpja.consultar_cnpj(cnpj)
    return jsonify(resultado)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Obtém a porta da variável de ambiente ou usa a 5000
    app.run(host='0.0.0.0', port=port, debug=True)  # Vincula a 0.0.0.0 para escutar externamente
