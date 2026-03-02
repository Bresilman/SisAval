import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
import random
import itertools
import warnings
import traceback

class SolverEngine:
    """
    Motor de Otimização de Modelos (Solver) Multi-Estratégia.
    Corrigido: Respeito estrito às transformações permitidas e penalidades.
    """
    def __init__(self, dataset, target_col, candidate_cols):
        self.dataset = dataset
        self.target_col = target_col
        self.candidate_cols = candidate_cols
        
        # Configurações padrão
        self.method = 'genetic' 
        self.population_size = 30
        self.generations = 15
        
        # Limites e Penalidades
        self.max_vif = 10.0
        self.max_p = 0.10
        self.max_cond_no = 1000.0 
        self.min_normality_p = 0.05 
        
        self.use_vif_penalty = True
        self.use_pval_penalty = True
        self.use_cond_no_penalty = True
        self.use_normality_penalty = True 
        
        self.allowed_transforms = ['linear', 'log', 'square'] # Default
        
        self.top_models = []

    def run_optimization(self, progress_callback=None):
        print(f"\n[SolverEngine] --- INÍCIO ---")
        print(f"[SolverEngine] Método: {self.method}")
        print(f"[SolverEngine] Transforms Permitidos (Recebidos): {self.allowed_transforms}")
        
        # Validação Crítica: Se lista vazia, força linear
        if not self.allowed_transforms:
            print("[SolverEngine] Aviso: Nenhuma transformação selecionada. Forçando 'linear'.")
            self.allowed_transforms = ['linear']

        if self.method == 'stepwise':
            return self._run_stepwise(progress_callback)
        elif self.method == 'brute':
            return self._run_brute_force(progress_callback)
        else:
            return self._run_genetic(progress_callback)

    # --- ESTRATÉGIAS ---
    def _run_genetic(self, callback):
        population = self._initialize_population()
        
        for gen in range(self.generations):
            ranked_pop = self._evaluate_population(population)
            
            # Conta válidos (Score > 0)
            valid_models = [ind for ind in ranked_pop if ind['score'] > 0]
            valid_count = len(valid_models)
            
            best_score = valid_models[0]['score'] if valid_models else 0.0
            
            if callback: 
                callback(f"Gen {gen+1}/{self.generations}: {valid_count} válidos. Top R²: {best_score:.4f}")
            
            # Elitismo: Mantém os top 5 (mesmo que ruins, para não zerar população)
            self.top_models = ranked_pop[:5]
            
            next_gen = self.top_models[:] 
            while len(next_gen) < self.population_size:
                # Se não tem pais válidos suficientes, reinicia aleatórios para manter diversidade
                if len(valid_models) < 2:
                    next_gen.extend(self._initialize_population()[:(self.population_size - len(next_gen))])
                    break
                
                p1 = self._tournament(valid_models)
                p2 = self._tournament(valid_models)
                child = self._crossover(p1, p2)
                child = self._mutate(child)
                next_gen.append(child)
            population = next_gen
            
        return self._format_results(self.top_models)

    def _run_stepwise(self, callback):
        # Stepwise usa apenas LINEAR por definição, mas podemos permitir transforms se selecionados?
        # Por padrão stepwise é seleção de variáveis. Vamos manter simples.
        # Se o usuário quiser transforms no stepwise, precisaria pré-calcular colunas.
        # Vamos usar apenas 'linear' aqui para ser fiel ao método clássico.
        current_vars = list(self.candidate_cols)
        history = []
        
        while len(current_vars) > 0:
            if callback: callback(f"Stepwise: {len(current_vars)} vars...")
            genes = {col: 'linear' if col in current_vars else 'drop' for col in self.candidate_cols}
            res = self._fit_and_score(genes)
            if res['score'] > 0: history.append(res)
            
            model = res.get('stats_model')
            if not model: break
            
            pvals = model.pvalues.drop('const', errors='ignore')
            if pvals.empty: break
            
            if pvals.max() > self.max_p:
                current_vars.remove(pvals.idxmax())
            else:
                break
        
        history.sort(key=lambda x: x['score'], reverse=True)
        return self._format_results(history[:5])

    def _run_brute_force(self, callback):
        safe_cols = self.candidate_cols[:12] 
        best_models = []
        count = 0
        total = 2**len(safe_cols) - 1
        
        # Brute Force testa apenas inclusão/exclusão (Linear)
        # Se quiséssemos testar transforms, a combinatória explodiria.
        
        for r in range(1, len(safe_cols) + 1):
            for combo in itertools.combinations(safe_cols, r):
                count += 1
                if count % 200 == 0 and callback: callback(f"Brute: {count}/{total}...")
                
                genes = {col: 'linear' if col in combo else 'drop' for col in self.candidate_cols}
                res = self._fit_and_score(genes)
                if res['score'] > 0: best_models.append(res)
        
        best_models.sort(key=lambda x: x['score'], reverse=True)
        return self._format_results(best_models[:10])

    # --- CORE ---
    def _initialize_population(self):
        pop = []
        # FIX: Usar estritamente allowed_transforms
        choices = self.allowed_transforms + ['drop']
        
        for _ in range(self.population_size):
            genes = {col: random.choice(choices) for col in self.candidate_cols}
            # Garante pelo menos 1 var
            if all(v == 'drop' for v in genes.values()):
                # Escolhe uma aleatória para ativar com um transform permitido
                activator = random.choice(self.candidate_cols)
                genes[activator] = random.choice(self.allowed_transforms)
            pop.append({'genes': genes, 'score': 0})
        return pop

    def _evaluate_population(self, population):
        for ind in population:
            if ind.get('score', 0) != 0: continue
            res = self._fit_and_score(ind['genes'])
            ind.update(res)
        return sorted([i for i in population if i.get('score', -1) > -1], key=lambda x: x['score'], reverse=True)

    def _fit_and_score(self, genes):
        X = pd.DataFrame(index=self.dataset.index)
        features = []
        try:
            y = pd.to_numeric(self.dataset[self.target_col], errors='coerce').fillna(0)
            for col, trans in genes.items():
                if trans == 'drop': continue
                
                # FIX: Verificação de segurança se trans está em allowed (caso venha de crossover sujo)
                if trans not in self.allowed_transforms and trans != 'linear': 
                    trans = 'linear' # Fallback segura
                
                raw = pd.to_numeric(self.dataset[col], errors='coerce').fillna(0)
                
                if trans == 'linear': name, val = col, raw
                elif trans == 'log': name, val = f"ln_{col}", np.log(np.maximum(raw, 0.001))
                elif trans == 'square': name, val = f"{col}2", raw**2
                elif trans == 'inverse': name, val = f"inv_{col}", 1 / np.maximum(raw, 0.001)
                else: name, val = col, raw
                
                X[name] = val
                features.append(name)
            
            if X.empty: return {'score': -1}
            X_const = sm.add_constant(X)
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = sm.OLS(y, X_const).fit()
            
            score = model.rsquared_adj
            if np.isnan(score) or score <= 0: return {'score': 0.0001}
            
            # --- PENALIDADES ---
            # 1. P-Valor
            if self.use_pval_penalty:
                pvals = model.pvalues.drop('const', errors='ignore')
                if not pvals.empty and pvals.max() > self.max_p: 
                    score *= 0.7 # Penalidade forte
            
            # 2. VIF
            if self.use_vif_penalty and len(features) > 1:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        # Check rápido de singularidade
                        if np.linalg.cond(X.values) < 1/np.finfo(float).eps:
                            vifs = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
                            if max(vifs) > self.max_vif: score *= 0.8
                except: pass

            # 3. Condition Number
            if self.use_cond_no_penalty:
                if model.condition_number > self.max_cond_no: score *= 0.8

            # 4. Normalidade (JB/Shapiro)
            if self.use_normality_penalty:
                resid = model.resid
                try:
                    if len(resid) < 50: _, p_norm = stats.shapiro(resid)
                    else: _, p_norm = stats.jarque_bera(resid)
                    
                    # Se P < min_normality_p (ex: 0.05), FALHOU no teste de normalidade.
                    # Penalizamos para que o solver prefira modelos que passem (P > 0.05).
                    if p_norm < self.min_normality_p:
                        score *= 0.7 # Penalidade significativa para não-normalidade
                except: pass

            return {'score': score, 'stats_model': model, 'features': features, 'genes': genes}
            
        except: return {'score': -1}

    def _tournament(self, pop):
        competitors = random.sample(pop, min(len(pop), 3))
        return max(competitors, key=lambda x: x['score'])

    def _crossover(self, p1, p2):
        genes = {c: p1['genes'][c] if random.random()>0.5 else p2['genes'][c] for c in self.candidate_cols}
        return {'genes': genes, 'score': 0}

    def _mutate(self, ind):
        genes = ind['genes'].copy()
        if random.random() < 0.2: # Taxa de mutação um pouco maior
            c = random.choice(self.candidate_cols)
            # FIX: Usar estritamente allowed_transforms
            choices = self.allowed_transforms + ['drop']
            genes[c] = random.choice(choices)
        return {'genes': genes, 'score': 0}

    def _format_results(self, best_list):
        out = []
        for i, m in enumerate(best_list):
            if m.get('score', -1) <= 0: continue
            res = m['stats_model']
            out.append({
                'rank': i+1,
                'r2_adj': res.rsquared_adj,
                'aic': res.aic, 
                'formula': " + ".join(m['features']),
                'genes': m['genes'],
                'features': m['features']
            })
        return out