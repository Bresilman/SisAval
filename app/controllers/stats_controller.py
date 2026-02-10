import pandas as pd
import warnings
import threading
from tkinter import messagebox
import tkinter as tk
from app.engines.stats_engine import StatsEngine

class StatsController:
    def __init__(self, main_controller):
        # Keeps reference to main app to access other modules (Data, UI)
        self.main = main_controller
        self.engine = StatsEngine()
        
        # Shortcuts to other controllers/handlers if they exist in main
        self.data_handler = getattr(self.main, 'data_handler', None)
        self.validator = getattr(self.main, 'validator', None)
        # self.view will be set via register_view
        self.view = getattr(self.main, 'view', None)
        
        # Optimizer Engine reference
        self.optimizer_engine = getattr(self.main, 'optimizer_engine', None)

        self.current_data = None 
        self.dependent_var = None
        self.independent_vars = []

    def register_view(self, view):
        """
        Registers the Main Window view instance with this controller.
        Required for the controller to access UI widgets (inputs, tables).
        """
        self.view = view

    def calcular(self):
        """
        Método principal chamado pelo botão 'Calcular'.
        """
        print("StatsController: Iniciando fluxo de cálculo...")

        # 1. Recuperar Dados (DataHandler)
        if self.data_handler:
            self.current_data = self.data_handler.get_data()
        
        if self.current_data is None or self.current_data.empty:
            messagebox.showwarning("Atenção", "Tabela de dados vazia ou não carregada.")
            return

        # 2. Recuperar Variáveis da UI (Tab Data)
        try:
            tab_data = self.view.tab_data if hasattr(self.view, 'tab_data') else None
            if tab_data:
                # Variável Dependente (Y)
                if hasattr(tab_data, 'combo_y'): # Old UI style
                    self.dependent_var = tab_data.combo_y.get()
                elif hasattr(tab_data, 'get_selected_variables'): # New UI style
                    self.dependent_var, _ = tab_data.get_selected_variables()
                
                # Variáveis Independentes (X)
                self.independent_vars = []
                if hasattr(tab_data, 'listbox_x'): # Old UI style
                    idxs = tab_data.listbox_x.curselection()
                    self.independent_vars = [tab_data.listbox_x.get(i) for i in idxs]
                elif hasattr(tab_data, 'get_selected_variables'): # New UI style
                    _, self.independent_vars = tab_data.get_selected_variables()
                
                # Log Global
                self.use_log = False
                if hasattr(tab_data, 'var_log_global'):
                    self.use_log = tab_data.var_log_global.get()

        except Exception as e:
            print(f"Aviso: Erro ao ler widgets da UI: {e}")

        # 3. Validação de Seleção
        if not self.dependent_var or not self.independent_vars:
            messagebox.showwarning("Atenção", "Selecione a variável Dependente (Y) e as Independentes (X) na aba de Dados.")
            return

        # 4. Execução da Regressão
        try:
            stats_results = self.engine.executar_regressao(
                self.current_data,
                self.independent_vars,
                self.dependent_var,
                self.use_log
            )

            # 5. Atualizar UI com Resultados
            self.main.last_stats = stats_results
            
            # Atualiza aba de Regressão
            if hasattr(self.view, 'tab_regression') and hasattr(self.view.tab_regression, 'update_results'):
                 self.view.tab_regression.update_results(stats_results['Summary_Raw'], stats_results)
            
            # Atualiza Plots
            if hasattr(self.view, 'tab_plots') and hasattr(self.view.tab_plots, 'atualizar_variaveis'):
                self.view.tab_plots.atualizar_variaveis(self.current_data.columns.tolist())
            
            # Validação Automática
            if self.validator:
                rep = self.validator.validar(stats_results)
                if hasattr(self.view, 'tab_validation') and hasattr(self.view.tab_validation, 'update_all'):
                    self.view.tab_validation.update_all(stats_results, rep)
            
            # Prepara Calculadora
            if hasattr(self.view, 'tab_calculator') and hasattr(self.view.tab_calculator, 'build_inputs'):
                self.view.tab_calculator.build_inputs(self.independent_vars, stats_results.get('Dados_Utilizados'))

            print("Cálculo concluído com sucesso.")

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro Crítico", f"Falha ao calcular: {str(e)}")

    def estimar(self):
        """
        Método para a aba Calculadora.
        """
        try:
            if not hasattr(self.view, 'tab_calculator'): return
            
            inputs = {}
            # Coleta inputs da calculadora
            for k, entry in self.view.tab_calculator.inputs.items():
                val_str = entry.get().replace(',', '.')
                if val_str:
                    inputs[k] = float(val_str)
            
            res = self.engine.predizer_valor(inputs)
            
            self.view.tab_calculator.show_result(
                res['Valor_Central'], 
                res['IP_Min'], 
                res['IP_Max']
            )
            
            if hasattr(self.view, 'tab_validation') and hasattr(self.view.tab_validation, 'sub_precision'):
                amp = self.view.tab_validation.sub_precision.update_precision(res)
            
        except Exception as e:
            messagebox.showerror("Erro na Estimativa", str(e))

    # --- MÉTODOS DE OTIMIZAÇÃO ---

    def analisar_transformacoes(self):
        try:
            if not self.optimizer_engine:
                messagebox.showerror("Erro", "Motor de Otimização não encontrado.")
                return

            if self.data_handler:
                df = self.data_handler.get_data()
            else:
                return

            # Busca Variáveis na UI (Tentativa robusta)
            y = self.dependent_var
            # Se não estiver setado no controller, tenta ler da UI agora
            if not y and hasattr(self.view, 'tab_data'):
                 if hasattr(self.view.tab_data, 'combo_y'): y = self.view.tab_data.combo_y.get()
                 elif hasattr(self.view.tab_data, 'get_selected_variables'): y, _ = self.view.tab_data.get_selected_variables()

            logy = False # Simplificação
            
            if not y: 
                messagebox.showwarning("Aviso", "Selecione a variável Dependente (Y) na aba Dados.")
                return

            cand = [c for c in self.data_handler.get_numeric_columns() if c != y]
            
            res = self.optimizer_engine.analisar_melhores_transformacoes(df, cand, y, logy)
            
            top = tk.Toplevel(self.view)
            top.title("Análise de Transformações")
            top.geometry("600x400")
            
            from tkinter import ttk
            tr = ttk.Treeview(top, columns=("v","b","r","a"), show="headings")
            tr.pack(fill='both', expand=True)
            
            tr.heading("v", text="Variável")
            tr.heading("b", text="Melhor Transf.")
            tr.heading("r", text="Correlação (R)")
            tr.heading("a", text="Ação Sugerida")
            
            for r in res: 
                tr.insert("", "end", values=(r["Variável"], r["Melhor Transf."], f"{r['Correlação (R)']:.3f}", r["Ação"]))
                
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def otimizar_avancado(self, config):
        try:
            if not self.optimizer_engine:
                messagebox.showerror("Erro", "Motor de Otimização não encontrado.")
                return

            if self.data_handler:
                df = self.data_handler.get_data()
            else:
                return

            y = self.dependent_var
            # Fallback fetch
            if not y and hasattr(self.view, 'tab_data'):
                 if hasattr(self.view.tab_data, 'combo_y'): y = self.view.tab_data.combo_y.get()
                 elif hasattr(self.view.tab_data, 'get_selected_variables'): y, _ = self.view.tab_data.get_selected_variables()
            
            cand = list(config.get('constraints', {}).keys())
            
            if not y or not cand: 
                messagebox.showwarning("Aviso", "Variável dependente ou candidatas não definidas.")
                return
            
            self.view.config(cursor="watch")
            self.view.update()
            
            def worker():
                try:
                    results = self.optimizer_engine.encontrar_melhores_modelos(df, cand, y, config=config)
                    self.view.after(0, lambda: self._on_otimizacao_sucesso(results))
                except Exception as e:
                    self.view.after(0, lambda: self._on_otimizacao_erro(str(e)))

            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            
            messagebox.showinfo("Otimização Iniciada", "O processo está rodando em segundo plano.")

        except Exception as e: 
            self.view.config(cursor="")
            messagebox.showerror("Erro", str(e))

    def _on_otimizacao_sucesso(self, results):
        self.view.config(cursor="")
        self.main.melhores_modelos_cache = results
        
        try:
            tr = None
            if hasattr(self.view, 'tab_optimizer'):
                if hasattr(self.view.tab_optimizer, 'sub_results'):
                     tr = self.view.tab_optimizer.sub_results.tree
                elif hasattr(self.view.tab_optimizer, 'tree_res'):
                     tr = self.view.tab_optimizer.tree_res
            
            if tr:
                tr.delete(*tr.get_children())
                if not results:
                    messagebox.showwarning("Resultado", "Nenhum modelo encontrado.")
                else:
                    for i, m in enumerate(results):
                        tr.insert("", "end", iid=i, values=(m.get('Modelo','?'), m.get('Variaveis',''), f"{m.get('R2_Adj',0):.4f}", m.get('Status','Ok')))
            
            messagebox.showinfo("Concluído", "Otimização finalizada!")
                
        except Exception as e:
            print(f"Erro ao atualizar UI do otimizador: {e}")

    def _on_otimizacao_erro(self, msg):
        self.view.config(cursor="")
        messagebox.showerror("Erro na Otimização", msg)
    
    def carregar_modelo_otimizado(self, idx):
        try:
            if not hasattr(self.main, 'melhores_modelos_cache') or not self.main.melhores_modelos_cache:
                return
                
            mod = self.main.melhores_modelos_cache[idx]
            
            if hasattr(self.view.tab_data, 'var_log_global'):
                self.view.tab_data.var_log_global.set(mod.get('Log_Ativo', False))
            
            # Logic to update listbox selection would go here
            # Assuming basic compatibility
            
            self.calcular()
            if hasattr(self.view, 'notebook') and hasattr(self.view, 'tab_regression'):
                self.view.notebook.select(self.view.tab_regression)
            
        except Exception as e:
            messagebox.showerror("Erro ao carregar modelo", str(e))