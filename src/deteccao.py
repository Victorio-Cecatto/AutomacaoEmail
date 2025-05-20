import time
import logging
from pathlib import Path
from threading import Thread, Lock

class Deteccao:
    def __init__(self, config_json):
        self.stopped = True
        self.lock = Lock()
        self.arquivo = set()
        self.PASTA_MONITORADA = config_json.get('pasta_monitorada', 'Email')
        self.logger = logging.getLogger(__name__)

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.daemon = True
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            try:
                pasta_monitorada = Path(self.PASTA_MONITORADA)
                if not pasta_monitorada.exists():
                    self.logger.warning(f"Pasta monitorada não existe: {self.PASTA_MONITORADA}")
                    time.sleep(5)
                    continue

                for cc in pasta_monitorada.iterdir(): # Email de quem estará em cópia
                    if not cc.is_dir():
                        continue

                    for para in cc.iterdir(): # Email para quem será enviado
                        if not para.is_dir():
                            continue
                    
                        for arquivo in para.iterdir(): # Verifica se tem algum arquivo
                            if arquivo.is_dir() and arquivo.name == 'enviados': # Verifica se é uma pasta
                                continue
                            
                            with self.lock:
                                self.arquivo.add(arquivo)

                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {e}")
                time.sleep(5)