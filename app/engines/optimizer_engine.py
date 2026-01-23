import itertools
import pandas as pd
import numpy as np
from app.engines.stats_engine import StatsEngine
from app.config import settings

class OptimizerEngine:
    def __init__(self):
        self.stats = StatsEngine()

    def analisar_melhores_transformacoes(self, df, vars_x, var_y, usar_log_y=False):
        """
        Tests which transformation (Linear, Ln, Inv, Quad, Raiz) yields 
        the highest correlation with Y (or Ln Y).
        """
        sugestoes = []
        
        # Prepare Y
        y_data = df[var_y]
        if usar_log_y:
            valid_idx = y_data > 0
            y_data = np.log(y_data[valid_idx])
            df_temp = df.loc[valid_idx]
        else:
            df_temp = df.copy()

        transformations = {
            "Linear (x)": lambda x: x,
            "Logarítmica (Ln x)": lambda x: np.log(x) if (x > 0).all() else None,
            "Inversa (1/x)": lambda x: 1/x if (x != 0).all() else None,
            "Quadrática (x²)": lambda x: x**2,
            "Raiz Quad. (√x)": lambda x: np.sqrt(x) if (x >= 0).all() else None
        }

        for col in vars_x:
            best_r = 0
            best_name = "Linear (x)"
            
            x_raw = df_temp[col]
            
            for trans_name, func in transformations.items():
                try:
                    x_trans = func(x_raw)
                    if x_trans is not None and not np.isinf(x_trans).any():
                        corr = np.corrcoef(x_trans, y_data)[0, 1]
                        if abs(corr) > abs(best_r):
                            best_r = corr
                            best_name = trans_name
                except:
                    pass

            sugestoes.append({
                "Variável": col,
                "Melhor Transf.": best_name,
                "Correlação (R)": best_r,
                "Ação": "Manter" if best_name == "Linear (x)" else "Transformar"
            })

        return sorted(sugestoes, key=lambda x: abs(x['Correlação (R)']), reverse=True)

    def encontrar_melhores_modelos(self, df, all_vars_x, var_y, config=None):
        if not config: config = {}
        
        models_to_test = config.get('models_to_test', ['linear'])
        all_results = []

        for model_type in models_to_test:
            use_log = True if model_type == 'log' else False
            sub_config = config.copy()
            sub_config['current_model_type'] = model_type
            
            if config.get('method') == 'stepwise':
                res = self._stepwise_search(df, all_vars_x, config.get('locked', []), var_y, use_log, sub_config)
            else:
                locked = config.get('locked', [])
                candidates = [v for v in all_vars_x if v not in locked]
                res = self._brute_force_search(df, candidates, locked, var_y, use_log, sub_config)
            
            all_results.extend(res)

        return sorted(all_results, key=lambda x: x['R2_Adj'], reverse=True)[:30]

    def _brute_force_search(self, df, candidates, locked, var_y, usar_log, config):
        resultados = []
        # USE CONFIG VALUE
        limit = settings.OPTIMIZER_MAX_VARS_COMBO
        max_vars_combo = min(len(candidates), limit)
        
        if not candidates: rng = [0]
        else: rng = range(1, max_vars_combo + 1)

        for k in rng:
            for combo in itertools.combinations(candidates, k):
                lista_x = list(locked) + list(combo)
                res = self._test_model(df, lista_x, var_y, usar_log, config)
                if res: resultados.append(res)
        return resultados

    def _stepwise_search(self, df, all_vars, locked, var_y, usar_log, config):
        current = list(locked)
        remaining = [v for v in all_vars if v not in locked]
        history = []
        if current:
            res = self._test_model(df, current, var_y, usar_log, config)
            if res: history.append(res)
        while remaining:
            best_step = None; best_var = None
            for var in remaining:
                test_vars = current + [var]
                res = self._test_model(df, test_vars, var_y, usar_log, config)
                if res:
                    if best_step is None or res['R2_Adj'] > best_step['R2_Adj']:
                        best_step = res; best_var = var
            if best_step:
                prev_r2 = history[-1]['R2_Adj'] if history else -999
                if best_step['R2_Adj'] > prev_r2:
                    current.append(best_var); remaining.remove(best_var); history.append(best_step)
                else: break
            else: break
        return history

    def _test_model(self, df, lista_x, var_y, usar_log, config):
        try:
            res = self.stats.executar_regressao(df, lista_x, var_y, usar_log=usar_log)
            params = res['Params']; constraints = config.get('constraints', {})
            for var, coef in params.items():
                if var == 'const': continue
                expected = constraints.get(var, 0)
                if expected == 1 and coef < 0: return None
                if expected == -1 and coef > 0: return None
            if config.get('filter_p'):
                if any(p > 0.10 for var, p in res['P_values'].items() if var != 'const'): return None
            if config.get('filter_vif'):
                vifs = res['Diagnosticos'].get('VIF', {})
                if any(v > 10 for v in vifs.values()): return None
            mod_type = "Log-Log" if usar_log else "Linear"
            return {'Variaveis': ", ".join(lista_x), 'R2_Adj': res['R2_Ajustado'], 'Status': "✅ Coerente", 'Modelo': mod_type, 'Log_Ativo': usar_log}
        except: return None