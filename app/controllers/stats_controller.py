import tkinter as tk
from tkinter import messagebox
import threading

class StatsController:
    def __init__(self, main_controller):
        self.main = main_controller
        self.data_handler = self.main.data_handler
        self.stats_engine = self.main.stats_engine
        self.validator = self.main.validator
        self.optimizer_engine = self.main.optimizer_engine
        self.view = self.main.view

    def calcular(self):
        try:
            y = self.view.tab_data.combo_y.get()
            idxs = self.view.tab_data.listbox_x.curselection()
            x = [self.view.tab_data.listbox_x.get(i) for i in idxs]
            log = self.view.tab_data.var_log_global.get()

            if not y or not x: return messagebox.showwarning("Atenção", "Selecione Y e X.")

            df = self.data_handler.get_data()
            self.main.last_stats = self.stats_engine.executar_regressao(df, x, y, log)

            self.view.tab_regression.update_results(self.main.last_stats['Summary_Raw'], self.main.last_stats)
            if hasattr(self.view, 'tab_plots'): self.view.tab_plots.atualizar_variaveis(df.columns.tolist())
            
            rep = self.validator.validar(self.main.last_stats)
            self.view.tab_validation.update_all(self.main.last_stats, rep)
            self.view.tab_calculator.build_inputs(x, self.main.last_stats.get('Dados_Utilizados'))
            self.view.notebook.select(1)
        except Exception as e: messagebox.showerror("Erro", str(e))

    def estimar(self):
        try:
            inp = {}
            for k, e in self.view.tab_calculator.inputs.items():
                val = float(e.get().replace(',', '.'))
                inp[k] = val
            res = self.stats_engine.predizer_valor(inp)
            self.view.tab_calculator.show_result(res['Valor_Central'], res['IP_Min'], res['IP_Max'])
            
            amp = self.view.tab_validation.sub_precision.update_precision(res)
            self.view.tab_validation.sub_precision.update_boundaries(self.main.last_stats.get('Dados_Utilizados'), inp)
            self.view.tab_validation.sub_scoring.auto_select_precision(amp)
        except Exception as e: messagebox.showerror("Erro", str(e))

    # --- OTIMIZADOR COM THREADING (WORKER) ---
    def otimizar_avancado(self, config):
        """
        Executa a otimização em uma Thread separada para não travar a interface.
        """
        try:
            df = self.data_handler.get_data()
            y = self.view.tab_data.combo_y.get()
            cand = list(config['constraints'].keys())
            
            if not y or not cand: return
            
            # Muda cursor para 'aguarde'
            self.view.config(cursor="watch")
            self.view.update()
            
            # Define a função que rodará em background
            def worker():
                try:
                    # Cálculo pesado
                    results = self.optimizer_engine.encontrar_melhores_modelos(df, cand, y, config=config)
                    
                    # Agenda atualização da UI na thread principal
                    self.view.after(0, lambda: self._on_otimizacao_sucesso(results))
                except Exception as e:
                    self.view.after(0, lambda: self._on_otimizacao_erro(str(e)))

            # Dispara a thread
            t = threading.Thread(target=worker)
            t.daemon = True # Garante que a thread morre se fechar o app
            t.start()
            
            # Aviso opcional
            messagebox.showinfo("Robô Iniciado", "A otimização está rodando em segundo plano.\nVocê será avisado quando terminar.")

        except Exception as e: 
            self.view.config(cursor="")
            messagebox.showerror("Erro", str(e))

    def _on_otimizacao_sucesso(self, results):
        """Chamado quando a thread termina com sucesso."""
        self.view.config(cursor="") # Restaura cursor
        self.main.melhores_modelos_cache = results
        
        # Acessa a treeview corretamente (suporta layout com ou sem subtabs)
        try:
            if hasattr(self.view.tab_optimizer, 'sub_results'):
                tr = self.view.tab_optimizer.sub_results.tree
            else:
                tr = self.view.tab_optimizer.tree_res
                
            tr.delete(*tr.get_children())
            
            if not results:
                messagebox.showwarning("Resultado", "Nenhum modelo atendeu aos critérios.")
            else:
                for i, m in enumerate(results):
                    tr.insert("", "end", iid=i, values=(m['Modelo'], m['Variaveis'], f"{m['R2_Adj']:.4f}", m['Status']))
                
                # Foca na aba de resultados se houver
                if hasattr(self.view.tab_optimizer, 'notebook'):
                    self.view.tab_optimizer.notebook.select(1)
                    
                messagebox.showinfo("Concluído", "Otimização finalizada com sucesso!")
                
        except Exception as e:
            print(f"Erro ao atualizar UI: {e}")

    def _on_otimizacao_erro(self, msg):
        """Chamado quando a thread falha."""
        self.view.config(cursor="")
        messagebox.showerror("Erro na Otimização", msg)

    def carregar_modelo_otimizado(self, idx):
        mod = self.main.melhores_modelos_cache[idx]
        self.view.tab_data.var_log_global.set(mod.get('Log_Ativo', False))
        
        lb = self.view.tab_data.listbox_x
        lb.selection_clear(0, 'end')
        items = lb.get(0, 'end')
        for v in mod['Variaveis'].split(", "):
            if v in items: lb.selection_set(items.index(v))
        self.calcular()

    def analisar_transformacoes(self):
        try:
            df = self.data_handler.get_data()
            y = self.view.tab_data.combo_y.get()
            logy = self.view.tab_data.var_log_global.get()
            cand = [c for c in self.data_handler.get_numeric_columns() if c!=y]
            
            if not y: return
            
            res = self.optimizer_engine.analisar_melhores_transformacoes(df, cand, y, logy)
            
            top = tk.Toplevel(self.view); top.geometry("500x400")
            from tkinter import ttk # Import local caso falte
            tr = ttk.Treeview(top, columns=("v","b","r","a"), show="headings")
            tr.pack(fill='both', expand=True)
            for c in ("v","b","r","a"): tr.heading(c, text=c)
            for r in res: tr.insert("", "end", values=(r["Variável"], r["Melhor Transf."], f"{r['Correlação (R)']:.3f}", r["Ação"]))
        except Exception as e: messagebox.showerror("Erro", str(e))