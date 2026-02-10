import time
import random
import csv
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÕES DO USUÁRIO ---

# URL da busca
BASE_SEARCH_URL = "https://www.vivareal.com.br/venda/ceara/fortaleza/lote-terreno_residencial/?utm_source=google&utm_medium=cpc&utm_campaign=pmax24br_gg_pc_bg_ld_ao_wb_re_vr_pf&gclsrc=aw.ds&gad_source=1&gad_campaignid=23100900930&gclid=CjwKCAiAssfLBhBDEiwAcLpwfrJQ8939g6AD-QOe3donthviihysuY1DMltw7yUvB5_SwZ2WcUyayRoCP2YQAvD_BwE"

# Intervalo de páginas
START_PAGE = 1
END_PAGE = 1

# Arquivo de saída
OUTPUT_FILE = "dados_vivareal_sync.csv"

# IMPORTANTE: Headless=False faz o navegador aparecer.
# Isso ajuda a "enganar" o site de que é um usuário real.
HEADLESS = False

# --------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
]

STEALTH_SCRIPTS = """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt'] });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    window.chrome = { runtime: {} };
"""

def get_existing_urls(filepath):
    if not os.path.exists(filepath):
        return set()
    urls = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('url'):
                    urls.add(row['url'])
    except Exception:
        pass
    return urls

def save_to_csv(data, filepath):
    file_exists = os.path.exists(filepath)
    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        fieldnames = [
            'id', 'titulo', 'preco', 'condominio', 'iptu', 'area', 'quartos', 
            'banheiros', 'vagas', 'bairro', 'endereco_completo', 'cidade', 
            'latitude', 'longitude', 'tipo', 'anunciante', 'telefones', 
            'datas_anuncio', 'url', 'data_coleta'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    print(f"      [+] Salvo.")

def clean_number(text):
    if not text: return 0
    clean = re.sub(r'[^\d,]', '', text)
    try:
        return float(clean.replace(',', '.'))
    except:
        return 0

def extract_details(browser, url):
    """Extrai dados de um imóvel específico (Modo Síncrono)."""
    # Cria um novo contexto para cada imóvel -> Limpa cookies e fingerprint
    context = browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        viewport={'width': 1920, 'height': 1080},
        locale='pt-BR'
    )
    context.add_init_script(STEALTH_SCRIPTS)
    page = context.new_page()

    try:
        print(f"   🏠 Acessando: {url}")
        page.goto(url, timeout=60000)
        
        # Delay maior e rolagem para parecer humano
        time.sleep(random.uniform(4, 7))
        page.mouse.wheel(0, 600)
        
        try:
            page.wait_for_selector('.price-info__values', timeout=15000)
        except:
            pass

        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        data = {}
        
        # 1. Dados Básicos
        data['url'] = url
        data['data_coleta'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['titulo'] = soup.select_one('h1.section-title').get_text(strip=True) if soup.select_one('h1.section-title') else "N/A"
        
        # 2. Valores
        price_elem = soup.select_one('.price-info__value, [data-testid="price-value"]')
        data['preco'] = clean_number(price_elem.get_text()) if price_elem else 0
        
        condo_elem = soup.select_one('[data-testid="condoFee"]')
        data['condominio'] = clean_number(condo_elem.get_text()) if condo_elem else 0
        
        iptu_elem = soup.select_one('[data-testid="iptu"]')
        data['iptu'] = clean_number(iptu_elem.get_text()) if iptu_elem else 0
        
        # 3. Características
        def get_feature(itemprop):
            el = soup.select_one(f'[itemprop="{itemprop}"] .amenities-item-text')
            if el:
                nums = re.findall(r'\d+', el.get_text())
                return int(nums[0]) if nums else 0
            return 0

        data['area'] = get_feature("floorSize")
        data['quartos'] = get_feature("numberOfRooms")
        data['banheiros'] = get_feature("numberOfBathroomsTotal")
        data['vagas'] = get_feature("numberOfParkingSpaces")
        
        # 4. Localização
        address_el = soup.select_one('[data-testid="location-address"]')
        data['endereco_completo'] = address_el.get_text(strip=True) if address_el else ""
        
        data['bairro'] = "N/A"
        data['cidade'] = "N/A"
        breadcrumbs = soup.select('.l-breadcrumb__item a')
        if len(breadcrumbs) >= 4:
            data['cidade'] = breadcrumbs[2].get_text(strip=True).replace("Apartamentos à venda em ", "")
            data['bairro'] = breadcrumbs[3].get_text(strip=True)
        
        # 5. Coordenadas
        iframe = soup.select_one('iframe[data-testid="map-iframe"]')
        data['latitude'] = None
        data['longitude'] = None
        if iframe:
            src = iframe.get('src', '')
            coords = re.search(r'q=(-?\d+\.\d+),(-?\d+\.\d+)', src)
            if coords:
                data['latitude'] = coords.group(1)
                data['longitude'] = coords.group(2)
                
        # 6. Datas e ID
        date_el = soup.select_one('[data-testid="listing-created-date"]')
        data['datas_anuncio'] = date_el.get_text(strip=True) if date_el else None
        
        codes_el = soup.select_one('[data-cy="ldp-propertyCodes-txt"]')
        if codes_el:
            id_match = re.search(r'Viva Real:\s*(\d+)', codes_el.get_text())
            data['id'] = id_match.group(1) if id_match else None
        
        type_tag = soup.select_one('.info-tags__unit-type')
        data['tipo'] = type_tag.get_text(strip=True) if type_tag else "Imóvel"
        
        return data

    except Exception as e:
        print(f"      ❌ Erro: {str(e)[:100]}")
        return None
    finally:
        context.close()

def get_search_links(browser, search_url):
    """Coleta links de uma página de busca."""
    context = browser.new_context(user_agent=random.choice(USER_AGENTS))
    page = context.new_page()
    links = []
    
    try:
        print(f"\n🔎 Lista: {search_url}")
        page.goto(search_url, timeout=60000)
        
        # Rolagem suave e longa para garantir carregamento
        for i in range(6):
            page.mouse.wheel(0, 4000)
            time.sleep(random.uniform(1, 2))
        
        hrefs = page.evaluate('''() => {
            const anchors = Array.from(document.querySelectorAll('li[data-cy="rp-property-cd"] a'));
            return anchors.map(a => a.getAttribute('href'));
        }''')
        
        for href in hrefs:
            if href and "imovel/" in href:
                full_url = "https://www.vivareal.com.br" + href if not href.startswith("http") else href
                links.append(full_url.split('?')[0])
                
    except Exception as e:
        print(f"   ⚠️ Erro na busca: {e}")
    finally:
        context.close()
        
    return list(set(links))

def main():
    existing_urls = get_existing_urls(OUTPUT_FILE)
    print(f"💾 Histórico: {len(existing_urls)} imóveis ignorados.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        
        for page_num in range(START_PAGE, END_PAGE + 1):
            sep = '&' if '?' in BASE_SEARCH_URL else '?'
            if "page=" in BASE_SEARCH_URL:
                current_url = re.sub(r'page=\d+', f'page={page_num}', BASE_SEARCH_URL)
            else:
                current_url = f"{BASE_SEARCH_URL}{sep}page={page_num}"
            
            # 1. Pega links
            page_links = get_search_links(browser, current_url)
            
            # 2. Filtra novos
            new_links = [l for l in page_links if l not in existing_urls]
            
            if not new_links:
                print(f"   [i] Nada novo na página {page_num}.")
                time.sleep(random.uniform(2, 4))
                continue
            
            print(f"   🚀 Processando {len(new_links)} imóveis...")
            
            # 3. Extrai um por um (Sequencial = Seguro)
            for i, url in enumerate(new_links):
                print(f"   [{i+1}/{len(new_links)}]", end="")
                data = extract_details(browser, url)
                
                if data:
                    save_to_csv(data, OUTPUT_FILE)
                    existing_urls.add(url)
                
                # Pausa longa entre imóveis para evitar bloqueio
                # Se for bloqueado de novo, aumente este valor.
                time.sleep(random.uniform(5, 10))
            
            print("   ...Resfriando motor para próxima página de busca...")
            time.sleep(random.uniform(10, 15))

        browser.close()
        print("\n🏁 Fim!")

if __name__ == "__main__":
    main()