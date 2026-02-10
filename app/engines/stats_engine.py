import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor, OLSInfluence
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
from scipy import stats
import pandas as pd
import numpy as np
import warnings
from app.config import settings

class StatsEngine:
    def __init__(self):
        self.model = None
        self.results = None
        self.x_vars = []
        self.y_var = ""
        self.usar_log = False
        self.logged_vars = []

    def executar_regressao(self, df, x_columns, y_column, usar_log=False):
        """
        Executa a regressão linear com tratamento robusto de dados.
        """
        # 1. Filtro de Warnings (Numpy/Pandas FutureWarnings)
        warnings.simplefilter(action='ignore', category=FutureWarning)

        # 2. Validações Básicas
        if df is None or df.empty:
            raise ValueError("Tabela de dados vazia.")

        self.x_vars = x_columns
        self.y_var = y_column
        self.usar_log = usar_log
        self.logged_vars = [] 
        
        x_unique = list(dict.fromkeys(x_columns))
        cols_needed = x_unique + [y_column]

        # 3. Sanitização Robusta (Crucial para CSVs com texto/números misturados)
        try:
            # Cria cópia para não afetar o original
            dados = df[cols_needed].copy()
            
            # Força conversão para números (texto vira NaN)
            for col in cols_needed:
                dados[col] = pd.to_numeric(dados[col], errors='coerce')
            
            # Remove linhas inválidas (NaN)
            dados = dados.dropna()
            
        except Exception as e:
            raise ValueError(f"Erro ao limpar dados: {str(e)}")

        if dados.empty:
            raise ValueError("Todas as linhas foram removidas. Verifique se os dados são numéricos (atenção para ponto vs vírgula).")

        # 4. Preparação das Variáveis
        X = dados[x_unique].copy()
        y = dados[y_column].copy()

        # 5. Aplicação de Log (Se solicitado)
        if usar_log:
            if (y <= 0).any():
                raise ValueError("Y contém valores <= 0. Não é possível aplicar Log Global.")
            y = np.log(y)

            for col in x_unique:
                # Pula colunas já transformadas ou binárias
                if col.startswith(('Ln_', 'Inv_', 'Quad_', 'Raiz_')): continue
                unique_vals = dados[col].unique()
                if len(unique_vals) <= 2 and set(unique_vals).issubset({0, 1, 0.0, 1.0}): continue
                if (dados[col] <= 0).any(): continue

                X[col] = np.log(X[col])
                self.logged_vars.append(col)

        # 6. Regressão
        X = sm.add_constant(X)
        
        try:
            self.model = sm.OLS(y, X)
            self.results = self.model.fit()
        except Exception as e:
             raise ValueError(f"Erro matemático ao ajustar modelo: {str(e)}")
        
        # 7. Cálculos Auxiliares
        diag = self._calcular_diagnosticos_blindado(self.results)
        importancia = self._calcular_importancia(X, y, self.results.params)
        elasticidade = self._calcular_elasticidade(dados[x_unique], dados[y_column], self.results.params, usar_log)

        # 8. Retorno no formato esperado pelo Controller antigo
        return {
            'R2': self.results.rsquared,
            'R2_Ajustado': self.results.rsquared_adj,
            'R_Correlation': np.sqrt(self.results.rsquared) if self.results.rsquared >= 0 else 0,
            'F_pvalue': self.results.f_pvalue,
            'Params': self.results.params,
            'P_values': self.results.pvalues,
            'Residuos': self.results.resid,
            'Valores_Previstos': self.results.fittedvalues,
            'Observado': y,
            'Diagnosticos': diag,
            'Importancia_Vars': importancia,
            'Elasticidade_Vars': elasticidade,
            'Summary_Raw': self.results.summary().as_text(),
            'N_Amostras': len(y),
            'N_Variaveis': len(x_unique),
            'Log_Ativo': usar_log,
            'Log_Vars_List': self.logged_vars,
            'Dados_Utilizados': dados
        }

    def predizer_valor(self, input_dict):
        if not self.results:
            raise Exception("Treine o modelo primeiro.")
        
        exog_names = self.results.model.exog_names
        exog_vals = []
        
        for name in exog_names:
            if name == 'const':
                exog_vals.append(1.0)
                continue

            val_final = 0.0
            
            # Lógica de Parsing de Variáveis Transformadas
            if name in input_dict:
                val_final = float(input_dict[name])
            
            elif name.startswith("Ln_") and name[3:] in input_dict:
                val_base = float(input_dict[name[3:]])
                if val_base <= 0: raise ValueError(f"{name[3:]} deve ser > 0.")
                val_final = np.log(val_base)
            
            # ... (outras transformações mantidas conforme seu código original) ...
            elif name.startswith("Inv_") and name[4:] in input_dict:
                val_base = float(input_dict[name[4:]])
                if val_base == 0: raise ValueError(f"{name[4:]} não pode ser 0.")
                val_final = 1 / val_base
            elif name.startswith("Quad_") and name[5:] in input_dict:
                val_base = float(input_dict[name[5:]])
                val_final = val_base ** 2
            elif name.startswith("Raiz_") and name[5:] in input_dict:
                val_base = float(input_dict[name[5:]])
                if val_base < 0: raise ValueError(f"{name[5:]} deve ser positivo.")
                val_final = np.sqrt(val_base)
            elif name.startswith("Num_") and name[4:] in input_dict:
                 val_final = float(input_dict[name[4:]])
            else:
                # Fallback para nomes limpos
                clean_name = name.split('_', 1)[-1] if '_' in name else name
                if clean_name in input_dict:
                        val_final = float(input_dict[clean_name])
                else:
                    # Se não encontrar, tenta ignorar se for variável dummy não marcada, ou alerta
                    # Para robustez, assumimos 0 se for erro
                    val_final = 0.0

            if name in self.logged_vars:
                if val_final <= 0: raise ValueError(f"Variável '{name}' deve ser > 0 para cálculo Log.")
                exog_vals.append(np.log(val_final))
            else:
                exog_vals.append(val_final)
        
        # Predição com Intervalo de Confiança
        # settings.STATS_ALPHA deve existir, senão usa 0.05 default
        alpha = getattr(settings, 'STATS_ALPHA', 0.05)
        pred = self.results.get_prediction([exog_vals])
        summary = pred.summary_frame(alpha=alpha)
        
        res = {
            'Valor_Central': summary['mean'][0],
            'IC_Min': summary['mean_ci_lower'][0], 
            'IC_Max': summary['mean_ci_upper'][0],
            'IP_Min': summary['obs_ci_lower'][0], 
            'IP_Max': summary['obs_ci_upper'][0]
        }

        if self.usar_log:
            for k, v in res.items():
                res[k] = np.exp(v)
                
        return res

    def _calcular_diagnosticos_blindado(self, results):
        diag = {}
        X_mat = np.asarray(results.model.exog, dtype=float)
        resid_vec = np.asarray(results.resid, dtype=float).flatten()
        vif_dict = {}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            col_names = results.model.exog_names
            for i in range(X_mat.shape[1]):
                c_name = col_names[i] if i < len(col_names) else f"Var{i}"
                if c_name != 'const':
                    try:
                        val = variance_inflation_factor(X_mat, i)
                        vif_dict[c_name] = val if np.isfinite(val) else 999.0
                    except: vif_dict[c_name] = 999.0
        diag['VIF'] = vif_dict
        try: diag['Shapiro_P'] = stats.shapiro(resid_vec)[1]
        except: diag['Shapiro_P'] = 0.0
        try: diag['BreuschPagan_P'] = het_breuschpagan(resid_vec, X_mat)[1]
        except: diag['BreuschPagan_P'] = 0.0
        try: diag['Durbin_Watson'] = durbin_watson(resid_vec)
        except: diag['Durbin_Watson'] = 0.0
        try: diag['Max_Cook'] = np.nanmax(OLSInfluence(results).cooks_distance[0])
        except: diag['Max_Cook'] = 0.0
        return diag

    def _calcular_importancia(self, X, y, params):
        imp = {}; total = 0; std_y = np.std(y)
        if std_y == 0: return {}
        for c in X.columns:
            if c != 'const':
                beta = abs(params[c] * (np.std(X[c])/std_y))
                imp[c] = beta; total += beta
        return {k: (v/total)*100 for k,v in imp.items()} if total else {}

    def _calcular_elasticidade(self, X, y, params, is_log):
        elast = {}; mean_y = np.mean(y)
        for c in X.columns:
            if c in params:
                beta = params[c]
                if is_log: elast[c] = beta
                else: elast[c] = beta * (np.mean(X[c])/mean_y) if mean_y!=0 else 0
        return elast