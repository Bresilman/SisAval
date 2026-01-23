import googlemaps
from datetime import datetime
import pandas as pd
import time

class GoogleGeoEngine:
    def __init__(self):
        self.client = None
        self.api_key = ""

    def connect(self, key):
        self.api_key = key
        try:
            self.client = googlemaps.Client(key=key)
            return True
        except:
            return False

    def calcular_distancias_matriz(self, df, lat_col, lon_col, targets):
        """
        Calcula a distância real de carro/tempo de cada imóvel para uma lista de Pólos.
        targets: dict {'Nome_Polo': (lat, lon), ...}
        """
        if not self.client: raise Exception("API não conectada")
        
        resultados = {name: [] for name in targets.keys()}
        
        # O Google permite max 25 destinos por chamada (Distance Matrix).
        # Vamos fazer um loop simples por origem para não estourar cotas complexas.
        
        count = 0
        for idx, row in df.iterrows():
            origin = (row[lat_col], row[lon_col])
            
            for name, dest_coords in targets.items():
                try:
                    # mode='driving' considera o trânsito histórico
                    # traffic_model='pessimistic' ajuda a ver gargalos
                    resp = self.client.distance_matrix(origin, dest_coords, mode='driving')
                    
                    if resp['rows'][0]['elements'][0]['status'] == 'OK':
                        # Pegamos distância em Metros
                        val = resp['rows'][0]['elements'][0]['distance']['value']
                        resultados[name].append(val)
                    else:
                        resultados[name].append(None)
                except:
                    resultados[name].append(None)
            
            count += 1
            # Pausa de segurança para não ser bloqueado por flood
            if count % 10 == 0: time.sleep(1)

        return resultados

    def analisar_densidade_servicos(self, df, lat_col, lon_col, raio=500):
        """
        Conta quantos estabelecimentos existem num raio X.
        Isso cria um 'Índice de Infraestrutura'.
        Custo: Places API é cara ($17/1000). Use com cuidado.
        """
        if not self.client: raise Exception("API não conectada")
        
        densidades = []
        tipos = ['school', 'hospital', 'supermarket', 'restaurant']
        
        for idx, row in df.iterrows():
            total_servicos = 0
            origin = (row[lat_col], row[lon_col])
            
            try:
                # Nearby Search
                for t in tipos:
                    res = self.client.places_nearby(location=origin, radius=raio, type=t)
                    # Conta quantos resultados vieram (max 20 por página)
                    total_servicos += len(res.get('results', []))
                
                densidades.append(total_servicos)
            except:
                densidades.append(0)
                
        return densidades