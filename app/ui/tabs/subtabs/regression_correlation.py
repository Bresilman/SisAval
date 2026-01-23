import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

class RegressionCorrelationSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.df = None
        self._setup_ui()

    def _setup_ui(self):
        # Main layout: Plot on Left, Analysis/Guide on Right
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill='both', expand=True)

        # 1. Plot Area (Left) - The Heatmap
        self.fr_plot = ttk.Frame(paned)
        paned.add(self.fr_plot, weight=3)
        
        self.fig = plt.Figure(figsize=(5, 5), dpi=90)
        self.canvas = FigureCanvasTkAgg(self.fig, self.fr_plot)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # 2. Analysis & Guide Area (Right) - The "Smart" Part
        fr_side = ttk.Frame(paned, padding=10)
        paned.add(fr_side, weight=1)

        # Save Button
        ttk.Button(fr_side, text="📷 Salvar Matriz", command=self.salvar_imagem).pack(fill='x', pady=(0, 10))

        # Diagnosis Section
        lbl_diag = ttk.Label(fr_side, text="🔍 Diagnóstico Automático", font=("Arial", 10, "bold"))
        lbl_diag.pack(anchor='w')

        self.txt_diagnosis = tk.Text(fr_side, width=35, height=15, font=("Arial", 9), bg="#f8f9fa", relief="flat")
        self.txt_diagnosis.pack(fill='both', expand=True, pady=5)

        # Educational Guide (Bottom of side panel)
        lbl_guide = ttk.Label(fr_side, text="📖 Como interpretar?", font=("Arial", 10, "bold"))
        lbl_guide.pack(anchor='w', pady=(10, 0))

        txt_guide = (
            "• Variável X vs Variável X:\n"
            "  - Ideal: COR BRANCA/FRACA (< 0.8).\n"
            "  - Perigo: COR FORTE (> 0.8).\n"
            "  -> Significa: Redundância (Multicolinearidade).\n"
            "  -> Ação: Remova uma delas.\n\n"
            "• Variável X vs Preço (Y):\n"
            "  - Ideal: COR FORTE (Vermelho ou Azul).\n"
            "  - Perigo: COR BRANCA (Próx. de 0).\n"
            "  -> Significa: Variável irrelevante.\n"
            "  -> Ação: Verifique o P-Valor."
        )
        lbl_guide_txt = tk.Label(fr_side, text=txt_guide, justify="left", anchor="nw", bg="#f0f0f0", relief="sunken", padx=5, pady=5, wraplength=250)
        lbl_guide_txt.pack(fill='x', expand=False)

    def update_corr(self, df):
        if df is None: return
        self.df = df
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        corr = df.corr()
        
        # Plot Heatmap
        cax = ax.matshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
        self.fig.colorbar(cax, shrink=0.8)
        
        # Labels
        ticks = range(len(corr.columns))
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(corr.columns, rotation=45, ha="left", fontsize=9)
        ax.set_yticklabels(corr.columns, fontsize=9)
        
        # Values in cells with contrast color
        for i in range(len(corr.columns)):
            for j in range(len(corr.columns)):
                val = corr.iloc[i, j]
                color = "white" if abs(val) > 0.6 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=8)

        self.fig.tight_layout()
        self.canvas.draw()

        # Run Automatic Diagnosis
        self._analyze_correlations(corr)

    def _analyze_correlations(self, corr):
        """Analyzes the matrix and writes a report on the side panel."""
        self.txt_diagnosis.delete(1.0, "end")
        self.txt_diagnosis.tag_config("critical", foreground="red", font=("Arial", 9, "bold"))
        self.txt_diagnosis.tag_config("warning", foreground="#cf8f02") # Dark Yellow
        self.txt_diagnosis.tag_config("good", foreground="green")

        cols = corr.columns
        problems_found = False
        
        # 1. Check Independent vs Independent (Multicollinearity)
        self.txt_diagnosis.insert("end", "--- Checagem de Conflitos (X vs X) ---\n")
        
        # We assume the last column is usually Y, but since we don't know for sure which is Y here,
        # we check ALL pairs. The user must use judgment for X vs Y.
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                val = corr.iloc[i, j]
                var1 = cols[i]
                var2 = cols[j]
                
                # Check for High Correlation (Multicollinearity Risk)
                if abs(val) >= 0.80:
                    problems_found = True
                    tag = "critical" if abs(val) >= 0.9 else "warning"
                    msg_type = "CRÍTICO" if abs(val) >= 0.9 else "ALERTA"
                    
                    self.txt_diagnosis.insert("end", f"⚠️ {msg_type}: ", tag)
                    self.txt_diagnosis.insert("end", f"{var1} e {var2}\n")
                    self.txt_diagnosis.insert("end", f"   Correlação: {val:.2f}\n")
                    self.txt_diagnosis.insert("end", "   Sugestão: Remova a menos importante.\n\n")

        if not problems_found:
            self.txt_diagnosis.insert("end", "✅ Nenhuma redundância grave detectada.\n\n", "good")

        # 2. General Tips
        self.txt_diagnosis.insert("end", "--- Dicas Gerais ---\n")
        self.txt_diagnosis.insert("end", "• Se 'Valor' tiver baixa correlação com alguma variável (ex: 0.05), o modelo pode ignorá-la.\n")
        self.txt_diagnosis.insert("end", "• Use a aba 'Dados' para remover variáveis conflitantes.")

    def salvar_imagem(self):
        f = filedialog.asksaveasfilename(defaultextension=".png")
        if f:
            self.fig.savefig(f, dpi=300)
            messagebox.showinfo("Sucesso", "Matriz salva!")