import re
import time
import random
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def clean_currency(value_str):
    if not value_str: return None
    # Remove R$, pontos e espaços, troca vírgula por ponto
    clean = re.sub(r'[^\d,]', '', value_str)
    return float(clean.replace(',', '.')) if clean else None

def extract_zap_data(url):
    with sync_playwright() as p:
        # Lança um navegador que parece real (não headless para evitar bloqueio inicial)
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"Acessando: {url}")
        page.goto(url, timeout=60000)
        
        # Espera inteligente: aguarda o preço aparecer, sinal que o JS carregou
        try:
            page.wait_for_selector(".price-info__values", state="visible", timeout=15000)
        except:
            print("Erro: Página demorou ou detectou bot.")
            return None

        # Pega o HTML final renderizado pelo navegador
        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        data = {}

        # 1. TÍTULO E ID
        data['titulo'] = soup.select_one("h1.section-title").get_text(strip=True) if soup.select_one("h1.section-title") else None
        
        # Captura IDs no texto (ex: "Código do anunciante: AP3154")
        desc_container = soup.select_one('[data-testid="description-container"]')
        if desc_container:
            text = desc_container.get_text()
            zap_id_match = re.search(r'Zap:\s*(\d+)', text)
            data['zap_id'] = zap_id_match.group(1) if zap_id_match else None

        # 2. PREÇOS (Venda, Condomínio, IPTU)
        price_section = soup.select_one(".price-info__values")
        if price_section:
            # O preço de venda geralmente é o primeiro destaque
            sale_elem = price_section.select_one(".value-item__value")
            data['preco_venda'] = clean_currency(sale_elem.get_text()) if sale_elem else None
            
            # Condominio e IPTU costumam ter data-testid ou ordem especifica
            condo_elem = price_section.select_one('[data-testid="condoFee"]')
            data['condominio'] = clean_currency(condo_elem.get_text()) if condo_elem else 0
            
            iptu_elem = price_section.select_one('[data-testid="iptu"]')
            data['iptu'] = clean_currency(iptu_elem.get_text()) if iptu_elem else 0

        # 3. CARACTERÍSTICAS (Área, Quartos, etc)
        # O site usa itemprop para metadados, o que é muito seguro de raspar
        def get_amenity(itemprop):
            elem = soup.select_one(f'[itemprop="{itemprop}"] .amenities-item-text')
            if elem:
                # Pega apenas os números (ex: "3 quartos" -> 3)
                nums = re.findall(r'\d+', elem.get_text())
                return int(nums[0]) if nums else 0
            return 0

        data['area_util'] = get_amenity("floorSize")
        data['quartos'] = get_amenity("numberOfRooms")
        data['banheiros'] = get_amenity("numberOfBathroomsTotal")
        data['vagas'] = get_amenity("numberOfParkingSpaces")
        data['suites'] = get_amenity("numberOfSuites")

        # 4. LOCALIZAÇÃO E COORDENADAS (O pulo do gato)
        address_elem = soup.select_one('[data-testid="location-address"]')
        data['endereco_completo'] = address_elem.get_text(strip=True) if address_elem else None

        # Pega Lat/Long do iframe do Google Maps
        iframe = soup.select_one('iframe[data-testid="map-iframe"]')
        if iframe and 'src' in iframe.attrs:
            src = iframe['src']
            # Regex para pegar q=-3.727245,-38.564612
            coords = re.search(r'q=(-?\d+\.\d+),(-?\d+\.\d+)', src)
            if coords:
                data['latitude'] = coords.group(1)
                data['longitude'] = coords.group(2)
        
        # 5. URL
        data['url_origem'] = url
        data['data_coleta'] = time.strftime("%Y-%m-%d %H:%M:%S")

        browser.close()
        return data

# --- TENTE RODAR COM UMA URL REAL AQUI ---
if __name__ == "__main__":
    # Substitua por uma URL real de um anúncio do Zap
    url_teste = "https://www.zapimoveis.com.br/imovel/venda-apartamento-3-quartos-vila-ellery-fortaleza-ce-65m2-id-2765168247/?source=ranking%2Crp" 
    
    # Se não tiver url, o script vai falhar, então certifique-se de colocar uma url válida
    if "COLE_A_URL" not in url_teste:
        resultado = extract_zap_data(url_teste)
        print("-" * 30)
        print(resultado)
        print("-" * 30)
    else:
        print("Por favor, coloque uma URL real do ZapImóveis na variável 'url_teste' no final do script.")