import gdown
import json
import re
import logging
from pypdf import PdfReader
from flask import Flask, request, jsonify
import requests

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def baixar_pdf(drive_id, output):
    url = f"https://drive.google.com/uc?export=download&id={drive_id}"
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(output, 'wb') as f:
                f.write(response.content)
            logging.info(f"PDF baixado como: {output}")
            return True
        else:
            logging.error(f"Erro ao baixar PDF, status code: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Erro ao baixar PDF: {e}")
        return False

def extrair_texto_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text()
    return texto

def extrair_vendas_avulsas(texto):
    padrao = r'Piso (\w+)\s+(\w+(?:\s+\w+)*)\s+(\w+(?:\s+\w+)*)\s+(\d+)\s+R\$\s+([\d.,]+)\s+R\$\s+[\d.,]+\s+R\$\s+([\d.,]+)'
    matches = re.findall(padrao, texto)
    vendas_avulsas = []
    for i, match in enumerate(matches, start=1):
        venda = {
            "id_concerto": i,
            "setor": match[0],
            "regiao": match[1],
            "tipo_ingresso": match[2],
            "tipo_desconto": "Nenhum",  
            "quantidade": int(match[3]),
            "valor": float(match[4].replace(',', '.')),
            "descontos": 0,  
            "total": float(match[5].replace(',', '.'))
        }
        vendas_avulsas.append(venda)
    return vendas_avulsas

def extrair_vendas_assinaturas(texto):
    padrao = r'Piso (\w+)\s+(\w+(?:\s+\w+)*)\s+(Série [\w\s]+)\s+(\w+)\s+(\d+)\s+R\$\s+([\d.,]+)'
    matches = re.findall(padrao, texto)
    vendas_assinaturas = []
    for i, match in enumerate(matches, start=1):
        valor_formatado = match[5].replace('.', '').replace(',', '.')
        assinatura = {
            "id_concerto": i,
            "setor": match[0],
            "regiao": match[1],
            "tipo": match[2],
            "tipo_ingresso": match[3],
            "quantidade": int(match[4]),
            "valor": float(valor_formatado)
        }
        vendas_assinaturas.append(assinatura)
    return vendas_assinaturas

def extrair_formas_pagto_vendas_avulsas(texto):
    padrao = r'(Cartão de Crédito Online Parcelado|PIX|Cartão de Crédito Online|INTI Wallet|Dinheiro|POS Cartão de Crédito)\s+R\$\s+([\d.,]+)\s+R\$\s+([\d.,]+)\s+R\$\s+([\d.,]+)\s+R\$\s+([\d.,]+)'
    matches = re.findall(padrao, texto)
    formas_pagto = []
    for match in matches:
        forma = {
            "forma_pagamento": match[0],
            "valor_bruto": float(match[1].replace('.', '').replace(',', '.')),
            "taxa_servico": float(match[2].replace('.', '').replace(',', '.')),
            "taxa_operacao": float(match[3].replace('.', '').replace(',', '.')),
            "valor_liquido": float(match[4].replace('.', '').replace(',', '.'))
        }
        formas_pagto.append(forma)
    return formas_pagto

def extrair_canais_vendas_avulsas(texto):
    padrao = r'(Administrativo|Bilheteria|Site)\s+R\$\s+([\d.,]+)\s+(\d+)\s+([\d.]+)\s*%'
    matches = re.findall(padrao, texto)
    canais = []
    for match in matches:
        canal = {
            "canal": match[0],
            "valor": float(match[1].replace('.', '').replace(',', '.')),
            "quantidade": int(match[2]),
            "porcentagem": float(match[3])
        }
        canais.append(canal)
    return canais

@app.route('/extrair-bordero', methods=['POST'])
def processar_pdf():
    data = request.json
    pdf_drive_id = data.get('drive_id')

    if not pdf_drive_id:
        return jsonify({"error": "drive_id não fornecido"}), 400

    output_pdf = "arquivo_baixado.pdf"
    baixar_pdf(pdf_drive_id, output_pdf)

    texto_extraido = extrair_texto_pdf(output_pdf)
    if texto_extraido:
        dados = {
            "vendas_avulsas": extrair_vendas_avulsas(texto_extraido),
            "vendas_assinaturas": extrair_vendas_assinaturas(texto_extraido),
            "forma_pagto_vendas_avulsas": extrair_formas_pagto_vendas_avulsas(texto_extraido),
            "canais_vendas_avulsas": extrair_canais_vendas_avulsas(texto_extraido)
        }
        return jsonify(dados)
    else:
        return jsonify({"error": "Falha ao extrair texto do PDF"}), 500

if __name__ == '__main__':
    app.run(debug=True)
