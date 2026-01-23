import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class CrawlerEngine:
    def __init__(self):
        self.driver = None

    def iniciar_coleta(self, url_inicial, qtd_paginas, pasta_destino, delay=5, callback_log=None):
        """
        Navega pelas páginas e salva o HTML.
        url_inicial: Link da busca (ex: olx.com.br/imoveis?q=ellery)
        qtd_paginas: Quantas páginas de resultados percorrer.
        """
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)

        self._log(callback_log, "Iniciando navegador (pode demorar um pouco)...")

        # Configuração do Chrome
        chrome_options = Options()
        # chrome_options.add_argument("--headless") # Descomente para não ver o navegador (mas sites bloqueiam mais fácil)
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        # User Agent para parecer humano
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

        try:
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
            
            atual_url = url_inicial
            
            for i in range(1, int(qtd_paginas) + 1):
                self._log(callback_log, f"Acessando página {i}...")
                self.driver.get(atual_url)
                
                # Espera carregar (Javascript)
                time.sleep(delay)
                
                # Rola a página para baixo para carregar imagens (Lazy Load)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Salva HTML
                nome_arq = f"pagina_{i}_{int(time.time())}.html"
                caminho_completo = os.path.join(pasta_destino, nome_arq)
                
                with open(caminho_completo, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                
                self._log(callback_log, f"Salvo: {nome_arq}")

                # Tenta achar o botão "Próxima Página"
                # Esta lógica varia por site. Se não achar, o usuário pode colar URLs paginadas manualmente,
                # ou implementamos lógica de detecção genérica.
                # Para simplificar este MVP, vamos tentar adivinhar a paginação na URL.
                
                if "page=" in atual_url:
                    # Tenta incrementar numero
                    # Isso é complexo de fazer genérico. 
                    # Vamos assumir que o usuário deve colar a URL base já paginada ou o crawler para.
                    pass
                elif "?" in atual_url:
                     atual_url += f"&o={i+1}" # Padrão OLX antigo
                else:
                     # Tenta clicar no botão "Próxima" (Lógica genérica de seta)
                     pass

        except Exception as e:
            self._log(callback_log, f"Erro: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
            self._log(callback_log, "Processo finalizado.")

    def _log(self, callback, msg):
        if callback:
            callback(msg)
        else:
            print(msg)