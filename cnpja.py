import http.client
import json
import logging

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para obter os dados de um CNPJ via API CNPJa
def obter_dados_cnpj(cnpj):
    conn = http.client.HTTPSConnection("api.cnpja.com")
    headers = {
        'Authorization': "916506d9-656d-42c2-8c58-285571d18a5a-47475ef5-1d25-412c-9274-23a8bd7748d8"
    }

    conn.request("GET", f"/office/{cnpj}", "", headers)
    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode("utf-8"))

# Função principal para processar a consulta de CNPJ
def consultar_cnpj(cnpj):
    try:
        dados_cnpj = obter_dados_cnpj(cnpj)
        return dados_cnpj
    except Exception as e:
        logging.error(f"Erro ao consultar CNPJ: {e}")
        return {"error": "Erro ao consultar o CNPJ"}
