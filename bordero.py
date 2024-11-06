import PyPDF2
import json
import re

# Função para extrair o texto do PDF
def extrair_texto_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        texto = ''
        for page in reader.pages:
            texto += page.extract_text()
        return texto

# Função para extrair vendas avulsas usando regex, sem omitir informações
def extrair_vendas_avulsas(texto):
    padrao = r'Piso (\w+)\s+(\w+(?:\s+\w+)*)\s+(\w+(?:\s+\w+)*)\s+(\d+)\s+R\$\s+([\d.,]+)\s+R\$\s+[\d.,]+\s+R\$\s+([\d.,]+)'
    matches = re.findall(padrao, texto)

    vendas_avulsas = []
    total_vendas_avulsas = 0
    total_quantidade_avulsas = 0

    for i, match in enumerate(matches, start=1):
        total = float(match[5].replace('.', '').replace(',', '.'))
        venda = {
            "id_concerto": i,
            "setor": match[0],
            "regiao": match[1],
            "tipo_ingresso": match[2],
            "tipo_desconto": "Nenhum",
            "quantidade": int(match[3]),
            "valor": float(match[4].replace(',', '.')),
            "descontos": 0,
            "total": total
        }
        vendas_avulsas.append(venda)
        total_vendas_avulsas += total
        total_quantidade_avulsas += int(match[3])

    qtd_avulsas_int = total_quantidade_avulsas
    val_avulsas_int = total_vendas_avulsas

    return vendas_avulsas, total_vendas_avulsas, total_quantidade_avulsas, qtd_avulsas_int, val_avulsas_int

# Função para extrair cortesias por nome com totalizador no final
def extrair_cortesias_por_nome(texto):
    cortesias = []
    capturando = False
    linhas = texto.splitlines()
    total_quantidades = 0

    for linha in linhas:
        if 'Cortesias por nome' in linha:
            capturando = True
            continue
        if capturando:
            if 'Total' in linha or not linha.strip():
                break
            partes = linha.rsplit(' ', 2)
            if len(partes) < 3 or not partes[-1].isdigit():
                continue
            setor = partes[0].strip()
            nome = partes[1].strip()
            quantidade = int(partes[2])
            total_quantidades += quantidade
            cortesias.append({
                "setor": setor,
                "nome": nome,
                "quantidade": quantidade
            })

    qtd_cortesia_int = total_quantidades

    return cortesias, total_quantidades, qtd_cortesia_int

# Função para extrair vendas de assinaturas usando regex
def extrair_vendas_assinaturas(texto):
    padrao = r'Piso (\w+)\s+(\w+(?:\s+\w+)*)\s+(Série [\w\s]+)\s+(\w+)\s+(\d+)\s+R\$\s+([\d.,]+)'
    matches = re.findall(padrao, texto)

    vendas_assinaturas = []
    total_assinaturas = 0
    total_quantidade_assinaturas = 0

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
        total_assinaturas += float(valor_formatado)
        total_quantidade_assinaturas += int(match[4])

    qtd_assinatura_int = total_quantidade_assinaturas
    val_assinatura_int = total_assinaturas

    return vendas_assinaturas, total_assinaturas, total_quantidade_assinaturas, qtd_assinatura_int, val_assinatura_int

# Função para extrair formas de pagamento das vendas avulsas
def extrair_formas_pagto_vendas_avulsas(texto):
    padrao = r'(Cartão de Crédito Online Parcelado|PIX|Cartão de Crédito Online|INTI Wallet|Dinheiro|POS Cartão de Crédito)\s+R\$\s+([\d.,]+)\s+R\$\s+([\d.,]+)\s+R\$\s+([\d.,]+)\s+R\$\s+([\d.,]+)'
    matches = re.findall(padrao, texto)

    formas_pagto = []
    total_formas_pagto = 0

    for match in matches:
        valor_liquido = float(match[4].replace('.', '').replace(',', '.'))
        forma = {
            "forma_pagamento": match[0],
            "valor_bruto": float(match[1].replace('.', '').replace(',', '.')),
            "taxa_servico": float(match[2].replace('.', '').replace(',', '.')),
            "taxa_operacao": float(match[3].replace('.', '').replace(',', '.')),
            "valor_liquido": valor_liquido
        }
        formas_pagto.append(forma)
        total_formas_pagto += valor_liquido

    return formas_pagto, total_formas_pagto

# Função para extrair formas de pagamento das vendas de assinaturas
def extrair_formas_pagto_vendas_assinaturas(texto):
    padrao = r'(Cartão de Crédito Online|Boleto|Cartão de Crédito Online Parcelado)\s+R\$\s+([\d.,]+)\s+R\$\s+([\d.,]+)\s+R\$\s+([\d.,]+)\s+R\$\s+([\d.,]+)'
    matches = re.findall(padrao, texto)

    formas_pagto_assinaturas = []
    total_formas_pagto_assinaturas = 0

    for match in matches:
        valor_liquido = float(match[4].replace('.', '').replace(',', '.'))
        forma = {
            "forma_pagamento": match[0],
            "valor_bruto": float(match[1].replace('.', '').replace(',', '.')),
            "taxa_servico": float(match[2].replace('.', '').replace(',', '.')),
            "taxa_operacao": float(match[3].replace('.', '').replace(',', '.')),
            "valor_liquido": valor_liquido
        }
        formas_pagto_assinaturas.append(forma)
        total_formas_pagto_assinaturas += valor_liquido

    return formas_pagto_assinaturas, total_formas_pagto_assinaturas

# Função para extrair canais de vendas avulsas
def extrair_canais_vendas_avulsas(texto):
    padrao = r'(Administrativo|Bilheteria|Totem|Site)\s+R\$\s+([\d.,]+)\s+\d+\s+[\d.]+ %'
    matches = re.findall(padrao, texto)

    canais_vendas = []
    total_vendas_canais = 0

    for match in matches:
        valor = float(match[1].replace('.', '').replace(',', '.'))
        canal = {
            "canal": match[0],
            "valor": valor
        }
        canais_vendas.append(canal)
        total_vendas_canais += valor

    return canais_vendas, total_vendas_canais

# Função para gerar o JSON completo com o nó "totalizadores"
def gerar_json_completo(texto):
    # Extraindo vendas avulsas e totais
    vendas_avulsas, val_avulsas_ia, qtde_avulsas_ia, qtd_avulsas_int, val_avulsas_int = extrair_vendas_avulsas(texto)

    # Extraindo vendas de assinaturas e totais
    vendas_assinaturas, val_assinatura_ia, qtd_assinatura_ia, qtd_assinatura_int, val_assinatura_int = extrair_vendas_assinaturas(texto)

    # Extraindo cortesias e total
    cortesias, qtd_cortesia_ia, qtd_cortesia_int = extrair_cortesias_por_nome(texto)

    # Extraindo formas de pagamento das vendas avulsas
    forma_pagto_vendas_avulsas, total_formas_pagto = extrair_formas_pagto_vendas_avulsas(texto)

    # Extraindo formas de pagamento das vendas de assinaturas
    forma_pagto_vendas_assinaturas, total_formas_pagto_assinaturas = extrair_formas_pagto_vendas_assinaturas(texto)

    # Extraindo canais de vendas avulsas
    canais_vendas_avulsas, total_vendas_canais = extrair_canais_vendas_avulsas(texto)

    # Montando o JSON final com o nó totalizadores
    json_completo = {
        "vendas_avulsas": vendas_avulsas,
        "vendas_assinaturas": vendas_assinaturas,
        "forma_pagto_vendas_avulsas": forma_pagto_vendas_avulsas,
        "forma_pagto_vendas_assinaturas": forma_pagto_vendas_assinaturas,
        "cortesias_por_nome": cortesias,
        "canais_vendas_avulsas": canais_vendas_avulsas,
        "totalizadores": {
            "val_avulsas_int": val_avulsas_int,
            "qtd_avulsas_int": qtd_avulsas_int,
           
            "qtde_avulsas_ia": qtde_avulsas_ia,
            "val_avulsas_ia": val_avulsas_ia,

            "qtd_cortesia_int": qtd_cortesia_int,
            "qtd_cortesia_ia": qtd_cortesia_ia,

            "qtd_assinatura_int": qtd_assinatura_int,
            "qtd_assinatura_ia": qtd_assinatura_ia,

            "val_assinatura_int": val_assinatura_int,
            "val_assinatura_ia": val_assinatura_ia,
            
            "total_formas_pagto_vendas_avulsas": total_formas_pagto,
            "total_formas_pagto_vendas_assinaturas": total_formas_pagto_assinaturas,
            "total_vendas_canais": total_vendas_canais
        }
    }
    return json_completo

# Função principal para processar o arquivo PDF e retornar o JSON completo
def processar_bordero(pdf_path):
    try:
        # Extraindo o texto do PDF
        texto = extrair_texto_pdf(pdf_path)

        # Gerando o JSON completo
        json_gerado = gerar_json_completo(texto)

        # Retornando o JSON completo
        return json_gerado

    except Exception as e:
        return {"error": str(e)}
