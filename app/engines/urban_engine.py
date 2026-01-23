import osmnx as ox
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

class UrbanEngine:
    def __init__(self):
        # Configurações do OSM
        ox.settings.use_cache = True
        self.city_name = "Fortaleza, Ceará, Brazil"
        self.bairros_gdf = None

    def carregar_geometria_bairros(self):
        """Baixa o mapa vetorial dos bairros de Fortaleza."""
        try:
            # Baixa limites administrativos (admin_level=9 ou 10 costuma ser bairro no Brasil)
            tags = {'admin_level': '9'} # Pode variar, as vezes é 10
            # Alternativa: Baixar a cidade toda e fazer spatial join depois
            self.bairros_gdf = ox.features_from_place(self.city_name, tags={'admin_level': '10'})
            
            # Se não achar por admin_level, tenta por geometria geral da cidade e grid
            if self.bairros_gdf.empty:
                 self.bairros_gdf = ox.geocode_to_gdf(self.city_name)
                 
            return len(self.bairros_gdf)
        except Exception as e:
            print(f"Erro OSM: {e}")
            return 0

    def contar_infraestrutura(self):
        """
        Conta escolas, hospitais, etc. por bairro.
        Retorna um DataFrame: Bairro | Qtd_Escolas | Qtd_Hospitais | Score
        """
        tags = {
            'amenity': ['school', 'hospital', 'pharmacy', 'marketplace'],
            'shop': ['supermarket', 'mall'],
            'leisure': ['park']
        }
        
        # Baixa TUDO da cidade de uma vez (Rápido e Grátis)
        pois = ox.features_from_place(self.city_name, tags=tags)
        
        # Converte para projeção métrica para calcular densidade se precisar
        pois_proj = pois.to_crs(epsg=31984) # SIRGAS 2000 / UTM zone 24S (Fortaleza)
        
        # Contagem simples (exemplo didático - ideal seria Spatial Join com polígonos dos bairros)
        # Como não temos o polígono exato de cada bairro fácil aqui sem shapefile oficial,
        # vamos agrupar por proximidade ou usar o nome do bairro se o OSM tiver.
        
        # Simplificação: Retorna a contagem total e cria um índice fictício para teste
        # Num cenário real, você faria um 'sjoin' (Spatial Join) entre self.bairros_gdf e pois
        
        resumo = pois.groupby('amenity').size().to_dict()
        return resumo, pois

    def calcular_preco_medio_bairro(self, df_imoveis):
        """
        Pega o DataFrame do Scraper e agrupa por Bairro para achar o valor do m².
        """
        if 'Bairro' not in df_imoveis.columns or 'Valor_Unitario' not in df_imoveis.columns:
            return None
            
        stats = df_imoveis.groupby('Bairro')['Valor_Unitario'].agg(['median', 'count', 'std'])
        stats = stats[stats['count'] > 5] # Só bairros com dados suficientes
        stats.columns = ['Valor_Medio_m2', 'Amostras', 'Desvio']
        return stats.sort_values(by='Valor_Medio_m2', ascending=False)

    def gerar_ranking_unificado(self, df_precos, df_infra):
        """
        Cria o 'Score do Bairro'.
        Score = (Peso_Preco * Preco_Norm) + (Peso_Infra * Infra_Norm)
        """
        # Exemplo de lógica: Cruzar os dados pelo nome do bairro
        # (Requer normalização de texto: "Fatima" vs "Bairro de Fatima")
        
        # Retorna tabela final
        return df_precos # Por enquanto retorna só preços