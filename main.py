import os
import time
import json
import logging
from pytz import timezone
from datetime import datetime
from dotenv import load_dotenv
from src import Smtp, Deteccao

# Configuração de logging
def configure_logging():
    logging.basicConfig(
        filename='logs/.log', 
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    return logging.getLogger(__name__)

# Carregar configurações gerais do JSON
def load_config():
    with open('config/.json', encoding='utf8') as file:
        return json.load(file)

# Mover arquivo para a pasta 'enviados'
def mover_arquivo(arquivo):
    try:
        dt = datetime.now()
        tz = timezone('America/Sao_Paulo')
        dtSP = dt.astimezone(tz)
        dtStr = dtSP.strftime('%Y-%m-%d_%H-%M-%S')

        caminho_enviado = arquivo.parent / 'enviados'
        os.makedirs(caminho_enviado, exist_ok=True)

        # Novo nome do arquivo com timestamp
        novo_nome = f'{dtStr} {arquivo.name}'
        novo_arquivo = caminho_enviado / novo_nome

        arquivo.rename(novo_arquivo)
        logging.info(f'Arquivo movido para: {caminho_enviado}')

    except Exception as e:
        logging.exception(f"Erro ao mover arquivo para enviados: {e}")

def process_files(dominio):
    while True:
        if not detector.arquivo:
            time.sleep(1)
            continue

        arquivo = None
        
        try:
            arquivo = list(detector.arquivo)[0]
            destinatario = f'{arquivo.parts[-2] + dominio}'
            encaminhado = f'{arquivo.parts[-3] + dominio}'

            if arquivo.is_dir():
                time.sleep(3)
                    
            if smtp.enviar_email(destinatario, encaminhado, arquivo):
                mover_arquivo(arquivo)

                with detector.lock:
                    detector.arquivo.discard(arquivo)
        
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {arquivo}: {e}")

if __name__ == "__main__":
    # Carrega configurações
    logger = configure_logging()
    config = load_config()
    load_dotenv()

    DOMINIO = config.get('dominio', '')

    email = os.getenv('EMAIL')
    senha = os.getenv('SENHA')

    # Inicializa componentes
    detector = Deteccao(config)
    smtp = Smtp(email, senha)

    # Inicia o detector
    detector.start()

    try:
        process_files(DOMINIO)
    except Exception as e:
        logger.critical(f"Erro crítico: {e}")
    finally:
        detector.stop()