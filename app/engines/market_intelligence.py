import pandas as pd
import numpy as np

class MarketIntelligenceEngine:
    def __init__(self):
        pass

    def gerar_indices_bairro(self, df_big_data):
        """
        Recebe um DataFrame grande (ex: do Banco de Dados Histórico)
        e gera uma tabela de referência de valores por bairro.
        """
        if df_big_data is None or df_big_data.empty:
            return {}
            
        # Garante que temos Bairro e Valor
        if 'Bairro' not in df_big_data.columns or 'Valor_Unitario' not in df_big_data.columns:
            return {}

        # Agrupa por Bairro
        # Usamos a Mediana porque é menos sensível a outliers (mansões ou ruínas)
        stats = df_big_data.groupby('Bairro')['Valor_Unitario'].agg(['median', 'count', 'std'])
        
        # Filtra bairros com pouca representatividade (ex: menos de 3 amostras)
        stats = stats[stats['count'] >= 3]
        
        # Retorna um dicionário: {'Ellery': 2500.00, 'Monte Castelo': 2800.00}
        return stats['median'].to_dict()

    def enriquecer_dataset_com_indices(self, df_alvo, indices_bairro, nome_coluna="Indice_Valor_Bairro"):
        """
        Pega o DataFrame da sua avaliação (pequeno) e adiciona o valor médio do bairro
        como uma nova coluna (Variável X).
        """
        if df_alvo is None: return None
        
        # Cria a coluna nova mapeando o bairro
        # Se o bairro não existir no índice, usa a média global ou NaN (que depois tratamos)
        media_global = np.mean(list(indices_bairro.values())) if indices_bairro else 0
        
        def get_valor(bairro):
            # Tenta match exato ou parcial
            if not isinstance(bairro, str): return media_global
            
            # Busca direta
            if bairro in indices_bairro:
                return indices_bairro[bairro]
            
            # Busca aproximada (ex: "Vila Ellery" vs "Ellery")
            for b_key, val in indices_bairro.items():
                if b_key in bairro or bairro in b_key:
                    return val
            
            return media_global

        df_alvo[nome_coluna] = df_alvo['Bairro'].apply(get_valor)
        return df_alvo