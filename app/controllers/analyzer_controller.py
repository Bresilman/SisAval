import pandas as pd
import numpy as np
import threading
import traceback
import datetime
from tkinter import filedialog

from app.engines.stats_engine import StatsEngine
from app.engines.auditor_engine import NBRAuditor
from app.models.data_handler import DataHandler

try:
    from app.engines.solver_engine import SolverEngine 
except ImportError as e:
    print(f"Aviso: SolverEngine não disponível: {e}")
    SolverEngine = None

# Imports do Módulo de Laudos
try:
    from app.config.report_config import REPORT_CONFIG
    from app.engines.report_engine import ReportEngine
except ImportError as e:
    print(f"Aviso: Módulos de Laudo não disponíveis: {e}")
    REPORT_CONFIG = None
    ReportEngine = None


class AnalyzerController:
    """
    Controlador Maestro - SisAval Analista.
    Gerência o estado dos dados, as threads do solver, a lógica da calculadora
    e agora a orquestração da geração de laudos físicos (PDF).
    """
    def __init__(self):
        self.view = None
        self.data_handler = DataHandler()
        self.stats_engine = None
        self.dataset = None
        self.auditor = None
        self.solver = None 
        
        # Estado do Modelo Ativo
        self.active_model_features = [] 
        self.active_target_col = ""
        self.is_log_y = False 
        
        # Estado da Calculadora (Para envio ao Laudo)
        self.last_calc_inputs = {}
        self.last_calc_result = {}
        
    def register_view(self, view):
        self.view = view

    # --- GESTÃO DE DADOS ---
    def acao_carregar_dados(self):
        if not self.view or not self.view.winfo_exists(): return
        try:
            filepath = filedialog.askopenfilename(parent=self.view, 
                                                filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")])
        except Exception: return
        if not filepath: return
        
        try:
            if filepath.endswith('.csv'): self.dataset = pd.read_csv(filepath)
            else: self.dataset = pd.read_excel(filepath)
            
            # Normalização técnica de colunas (snake_case)
            self.dataset.columns = self.dataset.columns.str.strip().str.replace(' ', '_').str.lower()
            
            self.stats_engine = StatsEngine(self.dataset)
            self._atualizar_interface_dados()
            
        except Exception as e:
            if self.view and self.view.winfo_exists():
                self.view.show_error(f"Erro ao carregar dados: {str(e)}")

    def _atualizar_interface_dados(self):
        """Notifica todas as abas sobre a mudança no dataset."""
        if not self.view or not self.view.winfo_exists(): return
        try:
            self.view.tabs['Dados'].update_table(self.dataset)
            if 'Regressão' in self.view.tabs:
                self.view.tabs['Regressão'].update_variable_lists(list(self.dataset.columns))
            if 'Otimizador' in self.view.tabs:
                self.view.tabs['Otimizador'].update_candidates(list(self.dataset.columns))
        except KeyError: pass

    # --- ENGENHARIA DE CARACTERÍSTICAS ---
    def acao_transformar_coluna(self, col_name, method):
        if self.dataset is None: return
        try:
            df = self.dataset
            series = pd.to_numeric(df[col_name], errors='coerce').fillna(0)
            
            if method == 'log':
                df[f"ln_{col_name}"] = np.log(np.maximum(series, 0.001))
            elif method == 'quad':
                df[f"{col_name}_2"] = series ** 2
            elif method == 'sqrt':
                df[f"sqrt_{col_name}"] = np.sqrt(series)
            elif method == 'inv':
                df[f"inv_{col_name}"] = 1 / (series + 0.001)
            elif method == 'drop':
                df.drop(columns=[col_name], inplace=True)
            
            self.dataset = df
            self.stats_engine = StatsEngine(self.dataset)
            self._atualizar_interface_dados()
        except Exception as e: 
            if self.view: self.view.show_error(f"Erro na transformação: {str(e)}")

    def acao_criar_indice(self, new_name, method, columns):
        if self.dataset is None: return
        try:
            df = self.dataset
            subset = df[columns].apply(pd.to_numeric, errors='coerce').fillna(0)
            
            if method == 'sum_ln':
                log_subset = np.log(np.maximum(subset, 0.001))
                df[new_name] = log_subset.sum(axis=1)
            elif method == 'mean':
                df[new_name] = subset.mean(axis=1)
            elif method == 'sum':
                df[new_name] = subset.sum(axis=1)
                
            self.dataset = df
            self.stats_engine = StatsEngine(self.dataset)
            self._atualizar_interface_dados()
        except Exception as e: 
            if self.view: self.view.show_error(f"Erro ao criar índice: {str(e)}")

    def acao_calcular_formula(self, new_name, formula_str):
        """Avalia fórmulas personalizadas via string."""
        if self.dataset is None: return
        try:
            new_name = new_name.strip().replace(' ', '_')
            self.dataset[new_name] = self.dataset.eval(formula_str)
            # Saneamento Anti-Crash
            self.dataset[new_name] = self.dataset[new_name].replace([np.inf, -np.inf], 0).fillna(0)
            
            self.stats_engine = StatsEngine(self.dataset)
            self._atualizar_interface_dados()
        except Exception as e:
            if self.view: self.view.show_error(f"Erro na fórmula: {str(e)}")

    # --- OTIMIZADOR (THREADS) ---
    def acao_rodar_otimizador(self, target_col, candidate_cols, settings=None):
        if self.dataset is None or SolverEngine is None: return
        
        self._safe_update_status("Inicializando Solver...")
        
        def run_thread():
            try:
                solver = SolverEngine(self.dataset, target_col, candidate_cols)
                if settings:
                    solver.method = settings.get('method', 'genetic')
                    solver.population_size = settings.get('pop_size', 30)
                    solver.generations = settings.get('generations', 15)
                    solver.max_vif = float(settings.get('max_vif', 10.0))
                    solver.max_p = float(settings.get('max_p', 0.10))
                    solver.max_cond_no = float(settings.get('max_cond_no', 1000.0))
                    solver.min_normality_p = float(settings.get('min_normality_p', 0.05))
                    solver.allowed_transforms = settings.get('allowed_transforms', ['linear'])
                
                def on_progress(msg):
                    if self.view and self.view.winfo_exists():
                        self.view.after(0, lambda m=msg: self._safe_update_status(m))
                
                results = solver.run_optimization(progress_callback=on_progress)
                
                if self.view and self.view.winfo_exists():
                    self.view.after(0, lambda r=results: self._safe_display_results(r))
            except Exception as e:
                err = str(e)
                if self.view and self.view.winfo_exists():
                    self.view.after(0, lambda m=err: self._safe_update_status(f"Erro: {m}"))

        threading.Thread(target=run_thread, daemon=True).start()

    def _safe_update_status(self, msg):
        if self.view and self.view.winfo_exists() and 'Otimizador' in self.view.tabs:
            self.view.tabs['Otimizador'].set_status(msg)

    def _safe_display_results(self, results):
        if self.view and self.view.winfo_exists() and 'Otimizador' in self.view.tabs:
            self.view.tabs['Otimizador'].display_results(results)

    def acao_carregar_modelo_otimizado(self, model_data):
        if self.dataset is None: return
        df = self.dataset
        final_features = []
        
        for col, trans in model_data['genes'].items():
            if trans == 'drop': continue
            try:
                raw = pd.to_numeric(df[col], errors='coerce').fillna(0)
                if trans == 'linear': final_features.append(col)
                elif trans == 'log':
                    name = f"ln_{col}"
                    if name not in df.columns: df[name] = np.log(np.maximum(raw, 0.001))
                    final_features.append(name)
                elif trans == 'square':
                    name = f"{col}2"
                    if name not in df.columns: df[name] = raw ** 2
                    final_features.append(name)
                elif trans == 'inverse': 
                    name = f"inv_{col}"
                    if name not in df.columns: df[name] = 1 / np.maximum(raw, 0.001)
                    final_features.append(name)
            except: pass

        self.dataset = df
        self.stats_engine = StatsEngine(self.dataset)
        self._atualizar_interface_dados()
        
        try:
            if self.view and self.view.winfo_exists():
                self.view.tabs['Regressão'].set_variables_programmatically(final_features)
                self.acao_calcular_regressao()
                self.view.tab_view.set("Regressão")
        except: pass

    # --- CÁLCULOS E PREDICÃO ---
    def acao_calcular_regressao(self):
        if self.dataset is None: return
        try:
            tab_reg = self.view.tabs['Regressão']
            target = tab_reg.get_target_variable()
            vars = tab_reg.get_selected_features()
            if not target or not vars: return
            
            res = self.stats_engine.fit_ols(target, vars) 
            tab_reg.display_results(res.summary().as_text())
            
            self.auditor = NBRAuditor(res, self.dataset)
            report = self.auditor.run_full_audit()
            if 'Validação' in self.view.tabs: self.view.tabs['Validação'].update_audit(report)
            
            self.active_model_features = vars
            self.active_target_col = target
            self.is_log_y = target.startswith("ln_") or target.startswith("log_")
            
            # Limpa memória da calculadora antiga
            self.last_calc_inputs = {}
            self.last_calc_result = {}
            
            if 'Calculadora' in self.view.tabs: 
                self.view.tabs['Calculadora'].setup_inputs(vars)
        except Exception as e:
            if self.view: self.view.show_error(f"Erro no cálculo: {str(e)}")

    def acao_calcular_valor(self, inputs_dict):
        """Lógica da Calculadora - Converte inputs brutos para transformados."""
        if not self.stats_engine or not self.stats_engine.results: return
        try:
            X_new = {}
            extrapolated = False
            for feat in self.active_model_features:
                if feat == 'const': continue
                
                base_name = feat
                if feat.startswith("ln_"): base_name = feat[3:]
                elif feat.startswith("log_"): base_name = feat[4:]
                elif feat.startswith("inv_"): base_name = feat[4:]
                elif feat.endswith("2"): base_name = feat[:-1] if feat.endswith("2") else feat
                
                user_val = inputs_dict.get(feat, 0.0)
                
                try:
                    col_data = self.dataset[base_name]
                    if user_val < col_data.min() or user_val > col_data.max(): extrapolated = True
                except: pass
                
                final_val = user_val
                if feat.startswith("ln_") or feat.startswith("log_"):
                    final_val = np.log(np.maximum(user_val, 0.001))
                elif feat.endswith("2"):
                    final_val = user_val ** 2
                elif feat.startswith("inv_"):
                    final_val = 1 / np.maximum(user_val, 0.001)
                
                X_new[feat] = final_val
            
            pred = self.stats_engine.predict(X_new)
            summ = pred.summary_frame(alpha=0.20)
            mean, lower, upper = summ['mean'][0], summ['mean_ci_lower'][0], summ['mean_ci_upper'][0]
            
            if self.is_log_y: 
                mean, lower, upper = np.exp(mean), np.exp(lower), np.exp(upper)
            
            amp = (upper - lower) / 2
            perc = (amp / mean) * 100
            if perc <= 30: grade = "Grau III"
            elif perc <= 40: grade = "Grau II"
            elif perc <= 50: grade = "Grau I"
            else: grade = "Fora de Norma"
            
            res_data = {
                'value': mean, 
                'lower': lower, 
                'upper': upper, 
                'precision_grade': grade, 
                'extrapolated': extrapolated
            }
            
            # Persiste os resultados no Controlador para uso futuro (Laudo)
            self.last_calc_inputs = inputs_dict
            self.last_calc_result = res_data
            
            if 'Calculadora' in self.view.tabs: 
                self.view.tabs['Calculadora'].display_results(res_data)
        except Exception as e:
            if self.view: self.view.show_error(f"Erro na predição: {str(e)}")

    # --- INTEGRAÇÃO COM MÓDULO DE LAUDOS ---
    def acao_gerar_laudo(self, filepath, formato='pdf', opcoes_ui=None):
        """
        Coleta todo o estado da aplicação e monta o Payload (Super Dicionário)
        para enviá-lo ao Motor Gerador de Laudos.
        """
        if not ReportEngine or not REPORT_CONFIG:
            raise Exception("Módulos de geração de laudo (ReportEngine, FPDF) não estão disponíveis ou instalados.")
            
        if not self.auditor or not self.stats_engine or not self.stats_engine.results:
            raise Exception("Não há um modelo estatístico validado. Calcule a Regressão primeiro.")
            
        if not self.last_calc_result:
            raise Exception("Não há um valor estimado para o imóvel. Utilize a aba Calculadora primeiro.")
            
        # Reexecuta uma auditoria silenciosa para garantir dados atualizados (ou utiliza o cache)
        audit_report = self.auditor.run_full_audit()
        
        # Filtra a constante para exibição da equação
        x_cols = [c for c in self.stats_engine.model.exog_names if c != 'const']
        equacao_str = f"{self.active_target_col} = f(" + ", ".join(x_cols) + ")"
        
        # Montagem do Payload (O "Contrato" de Geração)
        payload = {
            "metadados": {
                "data_geracao": datetime.datetime.now().isoformat(),
                "versao_software": "SisAval Analista 2.0"
            },
            "imovel_avaliando": {
                "inputs_informados": self.last_calc_inputs,
                "valor_central": self.last_calc_result.get('value', 0.0),
                "limite_inferior": self.last_calc_result.get('lower', 0.0),
                "limite_superior": self.last_calc_result.get('upper', 0.0),
                "valor_adotado": self.last_calc_result.get('value', 0.0) 
            },
            "modelo_estatistico": {
                "variavel_dependente": self.active_target_col,
                "equacao": equacao_str,
                "r2_ajustado": self.stats_engine.results.rsquared_adj,
                "amostra_tamanho": int(self.stats_engine.results.nobs)
            },
            "auditoria_nbr": {
                "grau_fundamentacao": audit_report.get('fundamentacao', 'N/D'),
                "grau_precisao": self.last_calc_result.get('precision_grade', 'N/D'),
                "interpretacoes": audit_report.get('interpretations', ''),
                "outliers_removidos": [] 
            },
            "graficos_paths": {
                # Placeholder: Integração futura com a exportação temporária do Matplotlib
                "path_aderencia": "",
                "path_histograma": ""
            },
            "opcoes_ui": opcoes_ui or {}
        }
        
        # Inicia o Motor Físico
        engine = ReportEngine(payload, REPORT_CONFIG)
        
        if formato.lower() == 'pdf':
            engine.generate_pdf(filepath)
        else:
            raise NotImplementedError(f"Formato de exportação '{formato}' ainda não é suportado nesta versão.")