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

    for i, match in enumerate(matches, start=1):
        total = float(match[5].replace(',', '.'))
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

    # Adicionando o totalizador
    vendas_avulsas.append({
        "totalizador": "Total Vendas Avulsas",
        "total": total_vendas_avulsas
    })

    return vendas_avulsas

# Função para extrair cortesias por nome com totalizador no final, sem deixar linhas de fora
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

    # Adicionar totalizador no final
    cortesias.append({
        "setor": "Totalizador",
        "nome": "Total de Cortesias",
        "quantidade": total_quantidades
    })

    return cortesias

# Função para extrair vendas de assinaturas usando regex, sem omitir informações
def extrair_vendas_assinaturas(texto):
    padrao = r'Piso (\w+)\s+(\w+(?:\s+\w+)*)\s+(Série [\w\s]+)\s+(\w+)\s+(\d+)\s+R\$\s+([\d.,]+)'
    matches = re.findall(padrao, texto)

    vendas_assinaturas = []
    total_assinaturas = 0

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

    # Adicionando totalizador
    vendas_assinaturas.append({
        "totalizador": "Total Vendas Assinaturas",
        "total": total_assinaturas
    })

    return vendas_assinaturas

# Função para extrair as formas de pagamento das vendas avulsas, incluindo valores detalhados
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

    # Adicionando totalizador
    formas_pagto.append({
        "totalizador": "Total Formas de Pagamento Vendas Avulsas",
        "total": total_formas_pagto
    })

    return formas_pagto

# Função para gerar o JSON completo incluindo todas as informações
def gerar_json_completo(texto):
    vendas_avulsas = extrair_vendas_avulsas(texto)
    vendas_assinaturas = extrair_vendas_assinaturas(texto)
    forma_pagto_vendas_avulsas = extrair_formas_pagto_vendas_avulsas(texto)
    cortesias = extrair_cortesias_por_nome(texto)

    # Montando o JSON final com todas as informações
    json_completo = {
        "vendas_avulsas": vendas_avulsas,
        "vendas_assinaturas": vendas_assinaturas,
        "forma_pagto_vendas_avulsas": forma_pagto_vendas_avulsas,
        "cortesias_por_nome": cortesias
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
