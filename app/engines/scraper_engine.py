import os
import re
import pandas as pd
import json
from bs4 import BeautifulSoup
from datetime import datetime
import platform

class ScraperEngine:
    def __init__(self):
        self.config_file = "scrapers_config.json"
        self.profiles = self._load_configs()

    def _load_configs(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f: return json.load(f)
            except: return {}
        return {}

    # ... (Keep existing helpers get_file_date, limpar_numero, extract_from_json_ld) ...
    def get_file_date(self, path):
        try:
            if platform.system() == 'Windows': timestamp = os.path.getctime(path)
            else: stat = os.stat(path); timestamp = stat.st_mtime
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        except: return datetime.now().strftime('%Y-%m-%d')

    def limpar_numero(self, texto):
        if not texto: return 0.0
        clean = re.sub(r'[^\d,]', '', str(texto)).replace(',', '.')
        try: return float(clean)
        except: return 0.0

    def extract_from_json_ld(self, soup):
        # ... (Keep existing JSON-LD logic here, it is very good as a fallback) ...
        # If you need me to paste the JSON-LD logic again, let me know, 
        # but for brevity I'm focusing on the Profile logic below.
        return {} 

    def extract_by_profile(self, soup, profile):
        """Extracts data using a saved profile configuration."""
        data = {}
        for field, selector in profile.items():
            try:
                tag = selector.get('tag', 'div')
                attrs = {}
                if 'id' in selector: attrs['id'] = selector['id']
                if 'class' in selector: attrs['class'] = selector['class']
                if 'attrs' in selector: attrs.update(selector['attrs'])
                
                elem = soup.find(tag, attrs)
                if elem:
                    text = elem.get_text(" ", strip=True)
                    # Convert Numeric Fields
                    if field in ['Valor_Total', 'Area', 'Quartos', 'Vagas']:
                        data[field] = self.limpar_numero(text)
                    else:
                        data[field] = text
            except:
                pass
        return data

    def processar_html(self, caminho_arquivo):
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
        except: return []

        file_date = self.get_file_date(caminho_arquivo)
        
        # Strategy 1: JSON-LD (Best for major sites)
        data = self.extract_from_json_ld(soup)
        if data.get('Valor_Total', 0) > 0:
            data['Fonte'] = "JSON-LD (Auto)"
            data['Data_Arquivo'] = file_date
            if 'Area' in data and data['Area'] > 0:
                data['Valor_Unitario'] = round(data['Valor_Total']/data['Area'], 2)
            return [data]

        # Strategy 2: Check Saved Profiles
        # We try to see if any profile extracts valid data (Price > 0)
        for name, profile in self.profiles.items():
            p_data = self.extract_by_profile(soup, profile)
            if p_data.get('Valor_Total', 0) > 0:
                p_data['Fonte'] = f"Perfil: {name}"
                p_data['Data_Arquivo'] = file_date
                # Infer Unit Value
                if p_data.get('Area', 0) > 0:
                    p_data['Valor_Unitario'] = round(p_data['Valor_Total']/p_data['Area'], 2)
                
                # Fill missing keys with empty strings to avoid errors
                for k in ['Endereco', 'Bairro', 'Quartos', 'Vagas']:
                    if k not in p_data: p_data[k] = ""
                    
                return [p_data]

        # Strategy 3: Generic Regex Fallback (Last Resort)
        # ... (Keep existing Regex logic from previous iteration) ...
        return []

    def extrair_de_pasta(self, pasta):
        self.profiles = self._load_configs()
        
        if not os.path.exists(pasta): return pd.DataFrame()
        all_data = []
        for f in os.listdir(pasta):
            if f.endswith(('html', 'htm')):
                data = self.processar_html(os.path.join(pasta, f))
                all_data.extend(data)
        
        if not all_data: return pd.DataFrame()
        
        df = pd.DataFrame(all_data)
        
        # DROP DUPLICATES IN BATCH
        # We assume if Price and Area are identical, it's the same ad captured twice in the same folder
        df.drop_duplicates(subset=['Valor_Total', 'Area', 'Endereco'], inplace=True)
        
        return df