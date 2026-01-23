import pandas as pd
import numpy as np

class DataHandler:
    def __init__(self):
        self.df = None

    def carregar_arquivo(self, caminho):
        if not caminho:
            raise ValueError("Caminho vazio.")
            
        if caminho.endswith('.csv'):
            self.df = pd.read_csv(caminho)
        elif caminho.endswith(('.xls', '.xlsx')):
            self.df = pd.read_excel(caminho)
        else:
            raise ValueError("Formato não suportado. Use CSV ou Excel.")
        
        # Limpeza Inicial
        self.df.dropna(how='all', inplace=True)
        self.df.dropna(axis=1, how='all', inplace=True)
        
        # Limpeza Inteligente de Tipos
        self._limpar_tipos()
        
        return self.df

    def _limpar_tipos(self):
        """
        Tenta converter colunas para numérico (ex: moeda), 
        mas PRESERVA texto se não for número.
        """
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                # Tentativa 1: Conversão direta (se for '10', '20')
                try:
                    # Tenta converter limpando caracteres comuns de moeda (R$, pontos)
                    # Regex: Mantém apenas digitos, sinal de menos e virgula
                    clean_series = self.df[col].astype(str).str.replace(r'[^\d,-]', '', regex=True)
                    clean_series = clean_series.str.replace(',', '.')
                    
                    # Converte para numérico
                    converted = pd.to_numeric(clean_series, errors='raise') # Raise para cair no except se falhar
                    
                    # Se converteu com sucesso, salva
                    self.df[col] = converted
                except:
                    # Se deu erro, é porque é Texto Real (ex: "Padrão Alto").
                    # Mantemos como está (Object/String).
                    pass

    def map_categorical_to_numeric(self, col, mapping_dict):
        """
        Converte uma coluna de texto em números baseados em um dicionário.
        Ex: {'Alto': 3, 'Médio': 2}
        """
        if self.df is None or col not in self.df.columns:
            raise ValueError("Coluna não encontrada.")
            
        new_col_name = f"Num_{col}"
        
        # Map values. Values not in dict become NaN
        self.df[new_col_name] = self.df[col].map(mapping_dict)
        
        # Fill NaNs with 0 or drop? NBR suggests analysis. For now fill 0 if mapping fails.
        self.df[new_col_name].fillna(0, inplace=True)
        
        return new_col_name

    def aplicar_transformacao(self, col_origem, tipo):
        if self.df is None or col_origem not in self.df.columns:
            raise ValueError("Coluna não encontrada.")
            
        series = pd.to_numeric(self.df[col_origem], errors='coerce')
        novo_nome = f"{tipo}_{col_origem}"
        
        if tipo == "Ln": self.df[novo_nome] = np.log(series[series > 0])
        elif tipo == "Inv": self.df[novo_nome] = 1 / series[series != 0]
        elif tipo == "Quad": self.df[novo_nome] = np.power(series, 2)
        elif tipo == "Raiz": self.df[novo_nome] = np.sqrt(series[series >= 0])
            
        return novo_nome

    def gerar_dados_exemplo(self):
        np.random.seed(42)
        n = 50
        area = np.random.normal(360, 50, n)
        frente = np.random.normal(12, 2, n)
        valor = 2000 - (1.5 * area) + (100 * frente) + np.random.normal(0, 100, n)
        
        # Adiciona uma variável categórica para testar o sistema
        padroes = np.random.choice(["Baixo", "Normal", "Alto"], n)
        
        data = {
            'Area': np.abs(area),
            'Frente': np.abs(frente),
            'Padrao_Acabamento': padroes, # Coluna de Texto!
            'Valor_Unitario': np.abs(valor)
        }
        self.df = pd.DataFrame(data)
        return self.df

    def get_numeric_columns(self):
        """Retorna apenas colunas numéricas."""
        if self.df is None: return []
        return list(self.df.select_dtypes(include=[np.number]).columns)

    def get_text_columns(self):
        """Retorna apenas colunas de texto (categóricas)."""
        if self.df is None: return []
        return list(self.df.select_dtypes(include=['object', 'category']).columns)

    def get_unique_values(self, col):
        """Retorna valores únicos de uma coluna de texto."""
        if self.df is None: return []
        return self.df[col].unique().tolist()

    def get_data(self):
        return self.df