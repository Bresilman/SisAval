from bs4 import BeautifulSoup
import pandas as pd
import re

class BaseScraper:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.data = []

    def clean_currency(self, text):
        """Converte 'R$ 1.200,00' para 1200.00"""
        if not text: return 0.0
        try:
            # Remove tudo que não é digito ou virgula
            clean = re.sub(r'[^\d,]', '', str(text))
            # Troca virgula por ponto
            return float(clean.replace(',', '.'))
        except:
            return 0.0

    def clean_number(self, text):
        """Converte '120 m²' para 120.0"""
        if not text: return 0.0
        try:
            clean = re.sub(r'[^\d]', '', str(text))
            return float(clean)
        except:
            return 0.0

    def parse(self):
        """Método que deve ser sobrescrito pelos scrapers específicos"""
        raise NotImplementedError("Cada scraper deve implementar seu próprio parse()")

    def to_dataframe(self):
        return pd.DataFrame(self.data)