import re
import time
import random
import csv
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- CONFIGURAÇÕES GERAIS ---

# Intervalo de páginas para raspar
PAGINA_INICIAL = 11
PAGINA_FINAL = 20 

# URL da busca (Copie do navegador após aplicar os filtros)
URL_BUSCA_BASE = "https://www.vivareal.com.br/venda/ceara/fortaleza/lote-terreno_residencial/?transacao=venda&onde=%2CCear%C3%A1%2CFortaleza%2C%2C%2C%2C%2Ccity%2CBR%3ECeara%3ENULL%3EFortaleza%2C-3.73272%2C-38.527013%2C&tipos=lote-terreno_residencial&ordem=MOST_RECENT"

# Nome do arquivo onde os dados serão salvos
ARQUIVO_SAIDA = "imoveis_vivareal.csv"

# Modo "Segundo Plano":
# True = Navegador invisível (mais rápido, não atrapalha).
# False = Abre a janela do navegador (bom para ver o que está acontecendo se der erro).
RODAR_EM_SEGUNDO_PLANO = True 

# ----------------------------

# --- CONFIGURAÇÃO DE PROXIES (OPCIONAL) ---
# Proxies ajudam a mudar seu IP para evitar bloqueios.
# Se deixar a lista vazia, ele usará sua conexão normal.
# Formatos aceitos:
# - Sem senha: "http://ip:porta" 
# - Com senha: "http://usuario:senha@ip:porta"
PROXIES = [
    # Exemplo: "http://bob:password123@123.45.67.89:8000",
    # "http://10.10.1.10:3128",
]

# --- LISTA AVANÇADA DE USER-AGENTS ---
# Simula diferentes dispositivos para "enganar" o site
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
]

def clean_currency(value_str):
    if not value_str: return None
    clean = re.sub(r'[^\d,]', '', value_str)
    try:
        return float(clean.replace(',', '.'))
    except:
        return None

def get_scraped_urls(filename):
    if not os.path.isfile(filename): return set()
    scraped = set()
    try:
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'url_origem' in row and row['url_origem']:
                    scraped.add(row['url_origem'].strip())
    except: pass
    return scraped

def save_to_csv(data, filename):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = [
            'titulo', 'preco_venda', 'condominio', 'iptu', 'area_util', 
            'quartos', 'banheiros', 'vagas', 'endereco_completo', 'bairro',
            'latitude', 'longitude', 'datas_atualizacao', 'vivareal_id', 
            'url_origem', 'data_coleta'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    print(f"   [+] Salvo no CSV.")

def get_page_links(browser, url):
    """Acessa a lista de busca e pega os links dos cards."""
    
    # Configura proxy se disponível
    proxy_config = {"server": random.choice(PROXIES)} if PROXIES else None
    
    context = browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        viewport={'width': 1366, 'height': 768},
        proxy=proxy_config
    )
    
    page = context.new_page()
    
    links = []
    try:
        print(f"   🔍 Lendo lista: {url}")
        page.goto(url, timeout=60000)
        
        # Scroll para carregar imagens e triggers (lazy load)
        for _ in range(4):
            page.mouse.wheel(0, 3000)
            time.sleep(random.uniform(0.5, 1.5))
            
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        cards = soup.select('li[data-cy="rp-property-cd"] > a')
        
        for card in cards:
            href = card.get('href')
            if href:
                if not href.startswith('http'):
                    href = "https://www.vivareal.com.br" + href
                
                clean_href = href.split('?')[0]
                links.append(clean_href)
                
    except Exception as e:
        print(f"   [!] Erro na listagem: {e}")
    finally:
        context.close()
        
    return list(set(links))

def extract_property_data(browser, url):
    """Acessa o imóvel e pega os detalhes, datas e coordenadas."""
    print(f"   🏠 Extraindo: {url}")
    
    # Rotação de Proxy e Agente a cada imóvel
    proxy_config = {"server": random.choice(PROXIES)} if PROXIES else None
    
    context = browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        viewport={'width': 1920, 'height': 1080},
        proxy=proxy_config,
        locale="pt-BR"
    )
    
    # Script essencial para esconder que é um robô
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    page = context.new_page()
    data = {}
    
    try:
        page.goto(url, timeout=45000)
        time.sleep(random.uniform(2, 5)) # Delay humano
        
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # --- 1. DATAS ---
        data_text = None
        for elem in soup.find_all(string=re.compile(r'(Publicado|Atualizado|Criado)')):
            if len(elem) < 100:
                data_text = elem.strip()
                break
        
        data['datas_atualizacao'] = data_text if data_text else "Não encontrado"

        # --- 2. DADOS PRINCIPAIS ---
        data['titulo'] = soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None
        
        price_elem = soup.select_one('.price-info__value, [data-testid="price-value"]')
        data['preco_venda'] = clean_currency(price_elem.get_text()) if price_elem else None
        
        condo_elem = soup.select_one('.price-info__condo, [data-testid="condo-value"]')
        data['condominio'] = clean_currency(condo_elem.get_text()) if condo_elem else 0
        
        iptu_elem = soup.select_one('.price-info__iptu, [data-testid="iptu-value"]')
        data['iptu'] = clean_currency(iptu_elem.get_text()) if iptu_elem else 0
        
        # --- 3. ENDEREÇO E COORDENADAS ---
        address_elem = soup.select_one('.title__address, [data-testid="address-info-value"]')
        data['endereco_completo'] = address_elem.get_text(strip=True) if address_elem else None
        
        if data['endereco_completo']:
            parts = data['endereco_completo'].split('-')
            if len(parts) > 1:
                data['bairro'] = parts[1].split(',')[0].strip()
            else:
                data['bairro'] = None
        else:
            data['bairro'] = None

        iframe = soup.select_one('iframe[src*="google.com/maps"]')
        data['latitude'] = None
        data['longitude'] = None
        if iframe:
            src = iframe.get('src', '')
            match = re.search(r'q=(-?\d+\.\d+),(-?\d+\.\d+)', src)
            if match:
                data['latitude'] = match.group(1)
                data['longitude'] = match.group(2)

        # --- 4. CARACTERÍSTICAS ---
        def extract_number(text):
            nums = re.findall(r'\d+', text)
            return int(nums[0]) if nums else 0
        
        area_elem = soup.select_one('.js-area, [data-testid="area-value"]')
        data['area_util'] = extract_number(area_elem.get_text()) if area_elem else 0
        
        bed_elem = soup.select_one('.js-bedrooms, [data-testid="bedrooms-value"]')
        data['quartos'] = extract_number(bed_elem.get_text()) if bed_elem else 0
        
        bath_elem = soup.select_one('.js-bathrooms, [data-testid="bathrooms-value"]')
        data['banheiros'] = extract_number(bath_elem.get_text()) if bath_elem else 0
        
        park_elem = soup.select_one('.js-parking, [data-testid="parking-value"]')
        data['vagas'] = extract_number(park_elem.get_text()) if park_elem else 0

        data['vivareal_id'] = url.split('-id-')[-1].replace('/', '') if '-id-' in url else None
        data['url_origem'] = url
        data['data_coleta'] = time.strftime("%d/%m/%Y %H:%M")

        return data

    except Exception as e:
        print(f"   [!] Erro no detalhe: {e}")
        return None
    finally:
        context.close()

def main():
    print(f"🤖 Iniciando Crawler VivaReal")
    print(f"📂 Arquivo de saída: {ARQUIVO_SAIDA}")
    print(f"📄 Páginas: {PAGINA_INICIAL} até {PAGINA_FINAL}")
    print(f"🕵️  Modo invisível: {RODAR_EM_SEGUNDO_PLANO}")
    
    historico_urls = get_scraped_urls(ARQUIVO_SAIDA)
    print(f"♻️  {len(historico_urls)} imóveis já coletados anteriormente (serão pulados).")

    with sync_playwright() as p:
        # Aqui definimos se roda visível ou invisível
        browser = p.chromium.launch(
            headless=RODAR_EM_SEGUNDO_PLANO, 
            args=['--disable-blink-features=AutomationControlled', '--start-maximized']
        )
        
        for pagina in range(PAGINA_INICIAL, PAGINA_FINAL + 1):
            print(f"\n--- Processando PÁGINA {pagina} ---")
            
            separator = '&' if '?' in URL_BUSCA_BASE else '?'
            if "page=" in URL_BUSCA_BASE:
                url_pagina = re.sub(r'page=\d+', f'page={pagina}', URL_BUSCA_BASE)
            else:
                url_pagina = f"{URL_BUSCA_BASE}{separator}page={pagina}"
            
            links_da_pagina = get_page_links(browser, url_pagina)
            novos_links = [l for l in links_da_pagina if l not in historico_urls]
            
            if not novos_links:
                print("   [i] Nenhum imóvel novo nesta página.")
                continue
                
            print(f"   > Encontrados {len(novos_links)} novos imóveis para extrair.")
            
            for i, link in enumerate(novos_links):
                dados = extract_property_data(browser, link)
                if dados:
                    save_to_csv(dados, ARQUIVO_SAIDA)
                    historico_urls.add(link)
                
                time.sleep(random.uniform(3, 7))

            print("   ...Resfriando antes da próxima página...")
            time.sleep(random.uniform(5, 10))

        browser.close()
        print("\n✅ Coleta finalizada!")

if __name__ == "__main__":
    main()