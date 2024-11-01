from flask import Flask, request, jsonify
from flask_cors import CORS
import bordero
import cnpja
import os
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Inicialização da aplicação Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para aceitar requisições de qualquer origem

# Middleware para logging de requisições
@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    if request.is_json:
        logger.debug('Body: %s', request.get_json())

# Middleware para tratamento de erros
@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f'Erro não tratado: {str(error)}', exc_info=True)
    return jsonify({
        "error": "Erro interno do servidor",
        "message": str(error)
    }), 500

# Rota para verificar se o servidor está online
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Servidor online"}), 200

# Rota para extrair dados de um borderô
@app.route('/extrair-bordero', methods=['POST'])
def extrair_bordero():
    try:
        # Verifica se a requisição contém JSON
        if not request.is_json:
            return jsonify({
                "error": "Requisição inválida",
                "message": "O conteúdo deve ser JSON"
            }), 400

        # Obtém os dados do JSON
        data = request.get_json()
        logger.debug(f'Dados recebidos: {data}')

        # Verifica se borderoPath está presente
        if 'borderoPath' not in data:
            return jsonify({
                "error": "Dados inválidos",
                "message": "O campo 'borderoPath' é obrigatório"
            }), 400

        bordero_path = data['borderoPath']

        # Verifica se o arquivo existe
        if not os.path.exists(bordero_path):
            return jsonify({
                "error": "Arquivo não encontrado",
                "message": f"O arquivo não foi encontrado em: {bordero_path}"
            }), 404

        # Processa o borderô
        resultado = bordero.processar_bordero(bordero_path)

        # Verifica se houve erro no processamento
        if "error" in resultado:
            return jsonify({
                "error": "Erro no processamento",
                "message": resultado["error"]
            }), 400

        # Retorna os dados processados
        return jsonify(resultado), 200

    except Exception as e:
        logger.error(f'Erro ao processar requisição: {str(e)}', exc_info=True)
        return jsonify({
            "error": "Erro interno",
            "message": str(e)
        }), 500

# Rota para consultar dados de um CNPJ
@app.route('/consulta-cnpj/<cnpj>', methods=['GET'])
def consulta_cnpj(cnpj):
    try:
        if not cnpj:
            return jsonify({"error": "CNPJ não fornecido"}), 400

        if not cnpj.isdigit() or len(cnpj) != 14:
            return jsonify({"error": "CNPJ inválido"}), 400

        logger.info(f'Iniciando consulta de CNPJ: {cnpj}')
        resultado = cnpja.consultar_cnpj(cnpj)

        if "error" in resultado:
            logger.error(f'Erro ao consultar CNPJ: {resultado["error"]}')
            return jsonify(resultado), 400

        logger.info('Consulta de CNPJ concluída com sucesso')
        return jsonify(resultado), 200

    except Exception as e:
        logger.error(f'Erro ao consultar CNPJ: {str(e)}', exc_info=True)
        return jsonify({
            "error": "Erro ao consultar CNPJ",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    try:
        # Obtém a porta da variável de ambiente ou usa a 5000 como padrão
        port = int(os.environ.get('PORT', 5000))
        
        # Configurações adicionais
        config = {
            'host': '0.0.0.0',  # Permite conexões externas
            'port': port,
            'debug': os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
            'threaded': True,  # Habilita múltiplas threads
        }

        logger.info(f'Iniciando servidor na porta {port}')
        app.run(**config)
        
    except Exception as e:
        logger.critical(f'Erro ao iniciar o servidor: {str(e)}', exc_info=True)
        raise