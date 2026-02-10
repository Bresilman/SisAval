import re
import time
import random
import csv
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# 1. LISTA EXPANDIDA DE USER-AGENTS
# Simula diferentes sistemas operacionais e versões de navegadores
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
]

# 2. CONFIGURAÇÃO DE PROXIES (IP ROTATION)
# Se você tiver proxies pagos ou gratuitos, coloque-os aqui.
# Formato: "http://usuario:senha@ip:porta" ou "http://ip:porta"
PROXIES = [
    # "http://user:pass@123.45.67.89:8080",
    # "http://111.222.333.444:3128",
]

def clean_currency(value_str):
    if not value_str: return None
    clean = re.sub(r'[^\d,]', '', value_str)
    return float(clean.replace(',', '.')) if clean else None

def get_scraped_urls(filename="imoveis_zap.csv"):
    """Lê o CSV e retorna um conjunto de URLs que já foram coletadas para evitar duplicação."""
    if not os.path.isfile(filename):
        return set()
    
    scraped = set()
    try:
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'url_origem' in row and row['url_origem']:
                    scraped.add(row['url_origem'].strip())
    except Exception as e:
        print(f"   [!] Erro ao ler histórico: {e}")
    
    return scraped

def save_to_csv(data, filename="imoveis_zap.csv"):
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    print(f"   [+] Dados salvos em {filename}")

def get_listing_urls(browser, search_url):
    """Acessa a página de busca e coleta links."""
    # Seleciona um proxy aleatório se houver
    proxy_server = {"server": random.choice(PROXIES)} if PROXIES else None
    
    context = browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        viewport={'width': 1366, 'height': 768},
        proxy=proxy_server
    )
    page = context.new_page()
    
    print(f"🔍 Acessando busca: {search_url}")
    
    try:
        page.goto(search_url, timeout=60000)
        
        print("   ...Rolando a página para carregar anúncios...")
        for _ in range(5):
            page.mouse.wheel(0, 5000)
            time.sleep(random.uniform(0.5, 1.5))
        
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        links = set()
        cards = soup.select('li[data-cy="rp-property-cd"] > a')
        
        for card in cards:
            href = card.get('href')
            if href:
                full_link = href if href.startswith('http') else f"https://www.zapimoveis.com.br{href}"
                clean_link = full_link.split('?')[0] 
                links.add(clean_link)
                
        print(f"   ✅ Encontrados {len(links)} imóveis únicos nesta página.")
        return list(links)
        
    except Exception as e:
        print(f"   [!] Erro na busca: {e}")
        return []
    finally:
        context.close()

def extract_details(browser, url):
    """Extrai os dados da página de detalhe."""
    print(f"🏠 Processando: {url}")
    
    # Rotação de Proxy (IP) a cada requisição
    proxy_server = {"server": random.choice(PROXIES)} if PROXIES else None

    context = browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        viewport={'width': 1920, 'height': 1080},
        locale="pt-BR",
        proxy=proxy_server
    )
    
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    page = context.new_page()
    
    try:
        page.goto(url, timeout=60000)
        time.sleep(random.uniform(3, 6))
        
        page.wait_for_selector(".price-info__values", state="visible", timeout=20000)
        
        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        data = {}

        # 1. TÍTULO E ID
        title_elem = soup.select_one("h1.section-title")
        data['titulo'] = title_elem.get_text(strip=True) if title_elem else None
        
        desc_container = soup.select_one('[data-testid="description-container"]')
        if desc_container:
            text = desc_container.get_text()
            zap_id_match = re.search(r'Zap:\s*(\d+)', text)
            data['zap_id'] = zap_id_match.group(1) if zap_id_match else None
        else:
            data['zap_id'] = None

        # 2. PREÇOS
        price_section = soup.select_one(".price-info__values")
        if price_section:
            sale_elem = price_section.select_one(".value-item__value")
            data['preco_venda'] = clean_currency(sale_elem.get_text()) if sale_elem else None
            
            condo_elem = price_section.select_one('[data-testid="condoFee"]')
            data['condominio'] = clean_currency(condo_elem.get_text()) if condo_elem else 0
            
            iptu_elem = price_section.select_one('[data-testid="iptu"]')
            data['iptu'] = clean_currency(iptu_elem.get_text()) if iptu_elem else 0

        # 3. CARACTERÍSTICAS
        def get_amenity(itemprop):
            elem = soup.select_one(f'[itemprop="{itemprop}"] .amenities-item-text')
            if elem:
                nums = re.findall(r'\d+', elem.get_text())
                return int(nums[0]) if nums else 0
            return 0

        data['area_util'] = get_amenity("floorSize")
        data['quartos'] = get_amenity("numberOfRooms")
        data['banheiros'] = get_amenity("numberOfBathroomsTotal")
        data['vagas'] = get_amenity("numberOfParkingSpaces")
        data['suites'] = get_amenity("numberOfSuites")

        # 4. LOCALIZAÇÃO
        address_elem = soup.select_one('[data-testid="location-address"]')
        data['endereco_completo'] = address_elem.get_text(strip=True) if address_elem else None

        iframe = soup.select_one('iframe[data-testid="map-iframe"]')
        data['latitude'] = None
        data['longitude'] = None
        
        if iframe and 'src' in iframe.attrs:
            src = iframe['src']
            coords = re.search(r'q=(-?\d+\.\d+),(-?\d+\.\d+)', src)
            if coords:
                data['latitude'] = coords.group(1)
                data['longitude'] = coords.group(2)
        
        data['url_origem'] = url
        data['data_coleta'] = time.strftime("%Y-%m-%d %H:%M:%S")

        return data

    except Exception as e:
        # Tratamento de Exceção: Loga o erro mas não quebra o loop principal
        print(f"   [!] Erro ao processar imóvel (pode ser bloqueio): {e}")
        return None
        
    finally:
        context.close()

def run_crawler(search_urls):
    # Se o usuário passar apenas uma string, converte para lista
    if isinstance(search_urls, str):
        search_urls = [search_urls]

    # Verifica o histórico para retomar
    scraped_urls = get_scraped_urls()
    print(f"📂 Histórico carregado: {len(scraped_urls)} imóveis já coletados.")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized'
            ]
        )
        
        all_property_urls = []

        # 1. Coleta Links de TODAS as buscas primeiro
        for url in search_urls:
            print(f"\n>>> Coletando links da busca: {url}")
            urls_found = get_listing_urls(browser, url)
            all_property_urls.extend(urls_found)
            # Pausa pequena entre páginas de busca
            time.sleep(random.uniform(2, 5))
        
        # Remove duplicatas da própria busca (caso tenha o mesmo imóvel em buscas diferentes)
        all_property_urls = list(set(all_property_urls))
        
        # Filtra apenas URLs que ainda NÃO foram raspadas (contra o histórico)
        new_urls = [u for u in all_property_urls if u not in scraped_urls]
        
        if not new_urls:
            print("Todos os imóveis encontrados já foram coletados!")
            browser.close()
            return

        print(f"\n--- Iniciando extração de {len(new_urls)} novos imóveis (Total encontrado: {len(all_property_urls)}) ---\n")

        consecutive_errors = 0

        for i, prop_url in enumerate(new_urls):
            print(f"[{i+1}/{len(new_urls)}]")
            
            imovel_data = extract_details(browser, prop_url)
            
            if imovel_data:
                save_to_csv(imovel_data)
                consecutive_errors = 0 # Reseta contador de erros
            else:
                consecutive_errors += 1
                # Se falhar 3 vezes seguidas, pausa longa (pode ser bloqueio de IP)
                if consecutive_errors >= 3:
                    print("   [!!!] Muitos erros consecutivos. Pausando por 2 minutos para resfriar...")
                    time.sleep(120)
                    consecutive_errors = 0
            
            delay = random.uniform(5, 10)
            print(f"   ...Aguardando {delay:.1f}s...") 
            time.sleep(delay)

        browser.close()
        print("\n🏁 Processo finalizado!")

if __name__ == "__main__":
    # --- CONFIGURAÇÃO: LISTA DE BUSCAS ---
    # Adicione aqui todas as URLs de busca que você quer processar
    URLS_DA_BUSCA = [
        "https://www.vivareal.com.br/venda/ceara/fortaleza/bairros/vila-ellery/lote-terreno_residencial/",
        "",
        # "https://www.zapimoveis.com.br/venda/imoveis/ce+fortaleza++outro-bairro/",
    ]
    
    run_crawler(URLS_DA_BUSCA)