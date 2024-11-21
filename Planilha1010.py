import paramiko
import pandas as pd
import pyodbc
import time
import logging
import sys
from paramiko.ssh_exception import SSHException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ssh_tunnel.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def create_ssh_tunnel():
    ssh_config = {
        'hostname': '200.168.239.203',
        'port': 22,
        'username': 'dkp-it',
        'password': 'Assinatura@2024'
    }
    
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh_client.connect(
            hostname=ssh_config['hostname'],
            port=ssh_config['port'],
            username=ssh_config['username'],
            password=ssh_config['password'],
            timeout=30
        )
        
        # Configuração correta do túnel
        transport = ssh_client.get_transport()
        dest_addr = ('DBSERVER01.osesp.local', 1433)
        local_port = 1433
        transport.request_port_forward('127.0.0.1', local_port, dest_addr[0], dest_addr[1])
        
        logging.info("Túnel SSH estabelecido com sucesso")
        return ssh_client
        
    except Exception as e:
        logging.error(f"Erro ao criar túnel SSH: {str(e)}")
        if 'ssh_client' in locals():
            ssh_client.close()
        raise

def connect_to_db():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=127.0.0.1;"
        "DATABASE=dbOsespBilheteria_H;"
        "UID=dkp-it;"
        "PWD=Assinatura@2024"
    )
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            conn = pyodbc.connect(conn_str, timeout=30)
            logging.info("Conexão com banco de dados estabelecida")
            return conn
        except Exception as e:
            logging.error(f"Tentativa {attempt + 1} falhou: {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(2)
            else:
                raise

def process_excel_data(cursor, file_path):
    try:
        df = pd.read_excel(file_path)
        logging.info(f"Carregados {len(df)} registros do Excel")
        
        for index, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO dbo.tbConcertoPublicos (
                        id, uuid, id_concerto, assinante_emitido, avulso_emitido,
                        cerimonial_emitido, divulgacao_emitido, musicos_emitido,
                        plu_emitido, funcionarios_emitido, patrocinador_emitido,
                        permutas_emitido, gratuidade_emitido, total_emitido,
                        assinante_presente, avulso_presente, cerimonial_presente,
                        divulgacao_presente, musicos_presente, plu_presente,
                        funcionarios_presente, patrocinador_presente, permutas_presente,
                        gratuidade_presente, total_presente, visualizacao_internet,
                        publico_primeira_sessao, publico_segunda_sessao, criado_em,
                        atualizado_em, deletado_em
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                             ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, 
                row['id'], row['uuid'], row['id_concerto'], row['assinante_emitido'],
                row['avulso_emitido'], row['cerimonial_emitido'], row['divulgacao_emitido'],
                row['musicos_emitido'], row['plu_emitido'], row['funcionarios_emitido'],
                row['patrocinador_emitido'], row['permutas_emitido'], row['gratuidade_emitido'],
                row['total_emitido'], row['assinante_presente'], row['avulso_presente'],
                row['cerimonial_presente'], row['divulgacao_presente'], row['musicos_presente'],
                row['plu_presente'], row['funcionarios_presente'], row['patrocinador_presente'],
                row['permutas_presente'], row['gratuidade_presente'], row['total_presente'],
                row['visualizacao_internet'], row['publico_primeira_sessao'],
                row['publico_segunda_sessao'], row['criado_em'], row['atualizado_em'],
                row['deletado_em']
                )
                
                if (index + 1) % 100 == 0:
                    cursor.commit()
                    logging.info(f"Processados {index + 1} registros")
                    
            except Exception as e:
                logging.error(f"Erro ao processar linha {index}: {str(e)}")
                cursor.rollback()
                
        cursor.commit()
        logging.info("Processamento concluído com sucesso")
        
    except Exception as e:
        logging.error(f"Erro ao processar arquivo Excel: {str(e)}")
        raise

def main():
    ssh_client = None
    conn = None
    cursor = None
    
    try:
        ssh_client = create_ssh_tunnel()
        time.sleep(2)  # Aguardar estabilização do túnel
        
        conn = connect_to_db()
        cursor = conn.cursor()
        
        file_path = r'C:\Users\edhon\OneDrive\PARA\1 - Projetos\Clientes\Osesp\Relatório de Vendas por Evento_1010.xlsx'
        process_excel_data(cursor, file_path)
        
    except Exception as e:
        logging.error(f"Erro durante execução: {str(e)}")
        if cursor and conn:
            cursor.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        if ssh_client:
            ssh_client.close()
        logging.info("Processo finalizado")

if __name__ == "__main__":
    main()