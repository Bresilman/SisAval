import threading
import traceback
import time
from datetime import datetime
import random

class ScraperWorker(threading.Thread):
    """
    Background thread for scraping. 
    Generates data compatible with the 'Tabela de Dados' requirements.
    """
    def __init__(self, target, engine_instance, msg_queue):
        super().__init__()
        self.target = target # Can be str or list[str]
        self.engine = engine_instance
        self.queue = msg_queue
        self.daemon = True

    def run(self):
        # Normalize input to list
        urls_to_process = self.target if isinstance(self.target, list) else [self.target]
        total = len(urls_to_process)
        
        self.queue.put(("STATUS", f"Iniciando coleta de {total} URLs..."))
        
        try:
            for i, url in enumerate(urls_to_process):
                if not url: continue
                
                self.queue.put(("STATUS", f"Processando {i+1}/{total}: {url[:30]}..."))
                self.queue.put(("LOG", f"Acessando: {url}"))
                
                try:
                    # --- SIMULATION OF SCRAPING ---
                    # In production: self.engine.scrape(url)
                    time.sleep(random.uniform(0.5, 1.5)) 
                    
                    # Mock Data matching your required columns
                    result = {
                        "id": random.randint(1000, 9999), # Temp ID
                        "cidade": "Fortaleza",
                        "estado": "CE",
                        "tipo": random.choice(["Apartamento", "Casa", "Terreno"]),
                        "preco": random.randint(200000, 2000000),
                        "endereco": f"Rua Mock, {random.randint(1, 5000)}",
                        "bairro": random.choice(["Aldeota", "Meireles", "Cocó"]),
                        "area": random.randint(50, 300),
                        "frente": 0,
                        "profundidade": 0,
                        "quartos": random.randint(1, 4),
                        "suites": random.randint(1, 3),
                        "andar": random.randint(1, 20),
                        "banheiros": random.randint(1, 5),
                        "vagas": random.randint(1, 3),
                        "conservacao": random.choice(["Novo", "Bom", "Regular"]),
                        "latitude": -3.717 + random.uniform(-0.01, 0.01),
                        "longitude": -38.500 + random.uniform(-0.01, 0.01),
                        "url": url,
                        "telefone": "85999999999",
                        "access_date": datetime.now().strftime("%Y-%m-%d"),
                        "ad_age": random.randint(0, 30)
                    }
                    
                    self.queue.put(("DATA", result))
                    
                except Exception as sub_e:
                    self.queue.put(("ERROR", f"Falha em {url}: {str(sub_e)}"))
                
            self.queue.put(("STATUS", "Lote finalizado."))
            self.queue.put(("LOG", "Coleta concluída."))
            
        except Exception as e:
            self.queue.put(("ERROR", f"Erro Crítico: {str(e)}"))
            print(traceback.format_exc())
        
        finally:
            self.queue.put(("DONE", None))