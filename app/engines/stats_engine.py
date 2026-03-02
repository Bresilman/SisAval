import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

class StatsEngine:
    """
    Core Statistical Engine for SisAval.
    Handles OLS, WLS, and RLM estimations with NBR 14.653 compliance.
    """
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.model = None
        self.results = None
        self.model_type = 'OLS' 

    def _prepare_matrices(self, target_col, feature_cols):
        """Standardizes X (Design Matrix) and y (Target Vector)."""
        # Garante que os dados são numéricos, forçando conversão e lidando com erros
        try:
            X = self.data[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
            y = self.data[target_col].apply(pd.to_numeric, errors='coerce').fillna(0)
        except Exception as e:
            raise ValueError(f"Erro na conversão de dados: {e}")
        
        # Add constant (Intercept)
        X = sm.add_constant(X)
        return X, y

    def fit_ols(self, target_col, feature_cols):
        """Fits Standard Ordinary Least Squares (Method of Moments)."""
        X, y = self._prepare_matrices(target_col, feature_cols)
        self.model = sm.OLS(y, X)
        self.results = self.model.fit()
        self.model_type = 'OLS'
        return self.results

    def fit_rlm_defense(self, target_col, feature_cols, method='Tukey'):
        """Fits Robust Linear Model (RLM) for outlier defense."""
        X, y = self._prepare_matrices(target_col, feature_cols)
        
        if method == 'Tukey':
            norm = sm.robust.norms.TukeyBiweight()
        else:
            norm = sm.robust.norms.HuberT()

        self.model = sm.RLM(y, X, M=norm)
        self.results = self.model.fit()
        self.model_type = 'RLM'
        return self.results

    def fit_wls_hybrid(self, target_col, feature_cols, rlm_results):
        """
        Hybrid Methodology: Uses weights from RLM to drive WLS.
        FIX: Handles zero weights to prevent log(0) errors.
        """
        X, y = self._prepare_matrices(target_col, feature_cols)
        
        # Extrai pesos do RLM
        weights = rlm_results.weights
        
        # --- CORREÇÃO DO ERRO DE DIVISÃO POR ZERO ---
        # O statsmodels calcula o log-likelihood fazendo log(weights).
        # Pesos exatamente zero (outliers severos no Tukey) causam crash.
        # Substituímos zeros por um epsilon muito pequeno (1e-10).
        weights = np.maximum(weights, 1e-10)
        # --------------------------------------------
        
        self.model = sm.WLS(y, X, weights=weights)
        self.results = self.model.fit()
        self.model_type = 'WLS_Hybrid'
        return self.results

    # --- NOVO MÉTODO DE PREDIÇÃO ---
    def predict(self, input_dict):
        """
        Gera uma predição pontual e intervalo de confiança para um novo imóvel.
        Conforme o Manual Técnico, garante o alinhamento com as colunas do modelo (exog_names)
        e a adição segura da constante para evitar quebras matemáticas.
        """
        if self.results is None or self.model is None:
            raise ValueError("Nenhum modelo foi ajustado ainda.")
            
        # Converte o dicionário de entrada para DataFrame de 1 linha
        X_new = pd.DataFrame([input_dict])
        
        # Coleta as colunas exatas que o modelo statsmodels espera (incluindo 'const')
        model_cols = self.model.exog_names
        
        # Adiciona a constante explicitamente se o modelo exigir (Medida de Segurança)
        if 'const' in model_cols and 'const' not in X_new.columns:
            X_new['const'] = 1.0
            
        # Garante que todas as colunas estejam presentes (preenche com 0 caso falte algo, fallback)
        for col in model_cols:
            if col not in X_new.columns:
                X_new[col] = 0.0
                
        # Reordena para garantir que a matriz esteja idêntica ao treinamento
        X_new = X_new[model_cols]
        
        # Converte tudo para numérico (evita que strings quebrem a matriz)
        X_new = X_new.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        # Retorna o objeto PredictionResults (contém a média e os intervalos de confiança)
        return self.results.get_prediction(X_new)

class StepwiseSelector:
    """Advanced Feature Selection with 'Physical Sense' Logic."""
    def __init__(self, data):
        self.data = data

    def backward_elimination(self, target, candidates, restrictions=None, alpha=0.10):
        remaining = list(candidates)
        restrictions = restrictions or {}
        
        while len(remaining) > 0:
            engine = StatsEngine(self.data)
            results = engine.fit_ols(target, remaining)
            
            # 1. Check Physical Sense
            violator = self._check_signs(results, restrictions)
            if violator:
                remaining.remove(violator)
                continue
                
            # 2. Check P-Values
            pvals = results.pvalues.drop('const', errors='ignore')
            max_p = pvals.max()
            if max_p > alpha:
                worst_var = pvals.idxmax()
                remaining.remove(worst_var)
            else:
                break 
                
        return remaining

    def _check_signs(self, results, restrictions):
        params = results.params
        for var, expected_sign in restrictions.items():
            if var in params:
                coef = params[var]
                if expected_sign > 0 and coef < 0: return var
                if expected_sign < 0 and coef > 0: return var
        return None