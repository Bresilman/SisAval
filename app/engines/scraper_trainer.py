from bs4 import BeautifulSoup
import re
import json
import os

class ScraperTrainer:
    def __init__(self):
        self.config_file = "scrapers_config.json"
        self.configs = self._load_configs()

    def _load_configs(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {}
        return {}

    def save_profile(self, profile_name, selectors):
        """Salva um perfil de raspagem nomeado."""
        self.configs[profile_name] = selectors
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.configs, f, indent=4, ensure_ascii=False)

    def find_best_selector(self, soup, target_value):
        """
        Encontra o seletor CSS mais específico para um determinado texto/valor.
        Prioridade: ID > data-testid > class única > tag
        """
        target_str = str(target_value).strip()
        if not target_str: return None
        
        # 1. Busca exata no texto (ignorando espaços extras)
        # Regex flexível para moeda/números
        escaped = re.escape(target_str)
        # Se for numero, permite formatação (ex: 1000 -> 1.000)
        elements = soup.find_all(string=re.compile(escaped))
        
        if not elements:
            # Tenta limpar formatação do HTML para achar
            return None

        best_score = 0
        best_sel = None

        for text_node in elements:
            parent = text_node.parent
            if parent.name in ['script', 'style', 'html', 'head']: continue

            sel = {"tag": parent.name}
            score = 1
            
            # Check ID (Gold standard)
            if parent.get('id'):
                sel["id"] = parent.get('id')
                score = 100
            
            # Check data-testid (Silver standard - Modern Frameworks)
            elif parent.get('data-testid'):
                sel["attrs"] = {"data-testid": parent.get('data-testid')}
                score = 90
                
            # Check Class (Bronze standard)
            elif parent.get('class'):
                classes = parent.get('class')
                # Ignora classes de layout genérico
                valid_classes = [c for c in classes if not c in ['flex', 'row', 'col', 'container']]
                if valid_classes:
                    sel["class"] = valid_classes # Usa todas as classes válidas
                    score = 50 + len(valid_classes)
            
            if score > best_score:
                best_score = score
                best_sel = sel

        return best_sel

    def auto_calibrate(self, html_path, profile_name, samples):
        """
        samples: Dict {'Valor_Total': '1000', 'Area': '50', 'Quartos': '2', ...}
        """
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
        except: return False, "Erro ao ler arquivo"

        profile_config = {}
        found_count = 0
        
        for field, value in samples.items():
            if value:
                selector = self.find_best_selector(soup, value)
                if selector:
                    profile_config[field] = selector
                    found_count += 1
        
        if found_count > 0:
            self.save_profile(profile_name, profile_config)
            return True, f"Perfil '{profile_name}' criado com {found_count} campos mapeados."
        
        return False, "Não foi possível encontrar nenhum dos valores informados no HTML."