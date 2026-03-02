import customtkinter as ctk
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import scipy.stats as stats
import pandas as pd

class ValAnalysis(ctk.CTkFrame):
    """
    Sub-aba: Análise Estatística Detalhada.
    Implementa Proteção de Erros do Payload e Gerenciamento Estrito de Memória (Matplotlib).
    """
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.current_audit_data = None 
        
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)
        
        # --- COLUNA ESQUERDA (TEXTOS) ---
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        lbl_interp = ctk.CTkLabel(self.left_panel, text="🧠 Interpretação Detalhada:", font=ctk.CTkFont(weight="bold"))
        lbl_interp.pack(anchor="w", pady=(0, 5))
        
        self.txt_interp = ctk.CTkTextbox(self.left_panel, font=ctk.CTkFont(family="Arial", size=12), wrap="word", height=250)
        self.txt_interp.pack(fill="x", pady=(0, 10))
        
        lbl_sum = ctk.CTkLabel(self.left_panel, text="📋 Sumário Estatístico & VIF:", font=ctk.CTkFont(weight="bold"))
        lbl_sum.pack(anchor="w", pady=(0, 5))
        
        self.txt_summary = ctk.CTkTextbox(self.left_panel, font=ctk.CTkFont(family="Courier New", size=11), wrap="none")
        self.txt_summary.pack(fill="both", expand=True)

        # --- COLUNA DIREITA (GRÁFICOS) ---
        self.right_panel = ctk.CTkFrame(self, fg_color="white") 
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.ctrl_frame = ctk.CTkFrame(self.right_panel, fg_color="#f0f0f0", height=40)
        self.ctrl_frame.pack(fill="x", side="top")
        
        lbl_select = ctk.CTkLabel(self.ctrl_frame, text="Visualizar Gráfico:", text_color="black")
        lbl_select.pack(side="left", padx=10, pady=5)
        
        self.combo_charts = ctk.CTkComboBox(self.ctrl_frame, 
                                          values=[
                                              "Aderência (Observado x Estimado)", 
                                              "Histograma de Resíduos (Normalidade)",
                                              "Resíduos x Valores Ajustados (Heterocedasticidade)",
                                              "Matriz de Correlação (Colinearidade)"
                                          ],
                                          width=300,
                                          command=self._on_graph_change)
        self.combo_charts.pack(side="left", padx=5, pady=5)
        self.combo_charts.set("Aderência (Observado x Estimado)")

        self.plot_frame = ctk.CTkFrame(self.right_panel, fg_color="white")
        self.plot_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.canvas = None
        self.fig = None 
        self.lbl_placeholder = ctk.CTkLabel(self.plot_frame, text="Aguardando cálculo da regressão...", text_color="gray")
        self.lbl_placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def update_data(self, audit):
        """Trata o payload recebido e aplica Fallback em caso de erros."""
        if not audit: return
        self.current_audit_data = audit 
        
        self.txt_summary.delete("0.0", "end")
        self.txt_interp.delete("0.0", "end")
        
        # 1. Tratamento de Erros da Auditoria
        if audit.get("errors"):
            self.txt_interp.insert("0.0", "⚠️ ERRO NO PROCESSAMENTO:\n" + "\n".join(audit["errors"]))
            self.txt_summary.insert("0.0", "Sumário indisponível devido a falha estatística.")
            self._clear_matplotlib_memory()
            return

        # 2. Atualizar Textos em Sucesso
        summary_text = audit.get('summary_text', 'N/A')
        
        vif_df = audit.get('variables', None)
        if isinstance(vif_df, pd.DataFrame) and not vif_df.empty and 'vif' in vif_df.columns:
            vif_table = "\n\n" + "="*78 + "\n"
            vif_table += f"{'ANÁLISE DE MULTICOLINEARIDADE (VIF)':^78}\n"
            vif_table += "="*78 + "\n"
            vif_table += f"{'Variável':<30} | {'VIF':<10} | {'Status'}\n"
            vif_table += "-"*78 + "\n"
            
            for _, row in vif_df.iterrows():
                try:
                    vif_val = float(row['vif'])
                    if np.isinf(vif_val):
                        status, str_val = "CRÍTICO (Inf)", "Inf"
                    elif np.isnan(vif_val):
                        status, str_val = "N/A", "N/A"
                    else:
                        status = "OK" if vif_val < 10 else "ALERTA"
                        str_val = f"{vif_val:.2f}"
                    vif_table += f"{row['name']:<30} | {str_val:<10} | {status}\n"
                except:
                    vif_table += f"{row['name']:<30} | {'N/A':<10} | N/A\n"
            summary_text += vif_table

        self.txt_summary.insert("0.0", summary_text)
        self.txt_interp.insert("0.0", audit.get('interpretations', ''))
        
        # 3. Atualizar Gráfico
        self._plot_current_selection()

    def _clear_matplotlib_memory(self):
        """Gerenciamento Crítico de Memória (Anti-Memory Leak)."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.fig:
            self.fig.clear()

    def _on_graph_change(self, choice):
        self._plot_current_selection()

    def _plot_current_selection(self):
        if not self.current_audit_data or 'plot_data' not in self.current_audit_data:
            return

        plot_data = self.current_audit_data.get('plot_data', {})
        if not plot_data: return

        if self.lbl_placeholder:
            self.lbl_placeholder.destroy()
            self.lbl_placeholder = None

        choice = self.combo_charts.get()
        
        # 1. Limpa Figura e Canvas Antigos
        self._clear_matplotlib_memory()
        
        # 2. Cria nova Figura
        self.fig = Figure(figsize=(5, 4), dpi=100)
        ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.15, right=0.95, top=0.90, bottom=0.15)
        
        # 3. Plotagem Condicional
        try:
            if "Aderência" in choice:
                self._plot_aderencia(ax, plot_data.get('y', []), plot_data.get('y_pred', []))
            elif "Histograma" in choice:
                self._plot_histograma(ax, plot_data.get('resid', []))
            elif "Resíduos x Valores" in choice:
                self._plot_resid_vs_fitted(ax, plot_data.get('y_pred', []), plot_data.get('resid', []))
            elif "Correlação" in choice:
                self._plot_correlation_matrix(ax, plot_data.get('corr_matrix'))
        except Exception as e:
            ax.text(0.5, 0.5, f"Erro ao plotar gráfico:\n{str(e)}", ha='center', va='center', color='red')
            
        # 4. Injeção no Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _plot_aderencia(self, ax, y_obs, y_pred):
        if len(y_obs) == 0 or len(y_pred) == 0: raise ValueError("Dados insuficientes")
        ax.scatter(y_obs, y_pred, alpha=0.6, edgecolors='b', label='Imóveis')
        min_val = min(min(y_obs), min(y_pred))
        max_val = max(max(y_obs), max(y_pred))
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Ideal')
        ax.set_title("Aderência (Real x Estimado)")
        ax.set_xlabel("Valor Real")
        ax.set_ylabel("Valor Calculado")
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_histograma(self, ax, resid):
        if len(resid) == 0: raise ValueError("Resíduos insuficientes")
        ax.hist(resid, bins=15, density=True, alpha=0.6, color='skyblue', edgecolor='black', label='Resíduos')
        try:
            xmin, xmax = ax.get_xlim()
            x = np.linspace(xmin, xmax, 100)
            mu, std = stats.norm.fit(resid)
            p = stats.norm.pdf(x, mu, std)
            ax.plot(x, p, 'k', linewidth=2, label='Normal')
        except: pass
        ax.set_title("Normalidade dos Erros")
        ax.set_xlabel("Erro")
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_resid_vs_fitted(self, ax, y_pred, resid):
        if len(y_pred) == 0 or len(resid) == 0: raise ValueError("Dados insuficientes")
        ax.scatter(y_pred, resid, alpha=0.6, edgecolors='purple')
        ax.axhline(0, color='black', linestyle='--', lw=1)
        ax.set_title("Resíduos vs Ajustados")
        ax.set_xlabel("Valor Calculado")
        ax.set_ylabel("Resíduo")
        ax.grid(True, alpha=0.3)

    def _plot_correlation_matrix(self, ax, corr_df):
        if corr_df is None or corr_df.empty:
            ax.text(0.5, 0.5, "Matriz indisponível", ha='center')
            return
        cax = ax.matshow(corr_df, cmap='coolwarm', vmin=-1, vmax=1)
        self.fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)
        cols = corr_df.columns
        ax.set_xticks(range(len(cols)))
        ax.set_yticks(range(len(cols)))
        ax.set_xticklabels(cols, rotation=45, ha="left", fontsize=7)
        ax.set_yticklabels(cols, fontsize=7)
        for i in range(len(cols)):
            for j in range(len(cols)):
                val = corr_df.iloc[i, j]
                text_color = "white" if abs(val) > 0.6 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=6)
        ax.set_title("Correlação (X)")