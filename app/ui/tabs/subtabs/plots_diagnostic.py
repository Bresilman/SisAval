import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class DiagnosticPlotsSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        fr_top = ttk.Frame(self, padding=5)
        fr_top.pack(fill='x')
        
        ttk.Button(fr_top, text="Influência (Cook)", command=self.plot_influence).pack(side='left', padx=2)
        ttk.Button(fr_top, text="Resíduos vs X", command=self.plot_resid_x).pack(side='left', padx=2)
        
        ttk.Label(fr_top, text="Var X:").pack(side='left', padx=5)
        self.cb_x = ttk.Combobox(fr_top, state="readonly", width=15)
        self.cb_x.pack(side='left')

        ttk.Button(fr_top, text="💾 Salvar", command=self.save_image).pack(side='right', padx=5)
        ttk.Button(fr_top, text="❓ Ajuda", command=self.show_help).pack(side='right')

        self.fig = plt.Figure(figsize=(6, 4), dpi=90)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def update_vars(self, cols):
        self.cb_x['values'] = cols
        if cols: self.cb_x.set(cols[0])

    def show_help(self):
        msg = (
            "DIAGNÓSTICO DO MODELO:\n\n"
            "1. INFLUÊNCIA (Cook's Distance):\n"
            "   - Identifica pontos que 'puxam' a reta de regressão.\n"
            "   - Pontos acima das linhas tracejadas vermelhas são influentes.\n"
            "   - Ação: Verifique se não é um erro de digitação.\n\n"
            "2. RESÍDUOS vs VARIÁVEL X:\n"
            "   - Ideal: Uma nuvem aleatória de pontos.\n"
            "   - Ruim: Formato de 'Funil' (erro aumenta com X) -> Heterocedasticidade.\n"
            "   - Ruim: Formato de 'U' (Curva) -> Precisa de transformação (ex: X²)."
        )
        messagebox.showinfo("Ajuda: Diagnóstico", msg)

    def save_image(self):
        f = filedialog.asksaveasfilename(defaultextension=".png")
        if f: self.fig.savefig(f, dpi=300)

    def plot_influence(self):
        stats = self.controller.last_stats
        if not stats: return messagebox.showwarning("Aviso", "Calcule a regressão primeiro.")

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        resid = stats['Residuos']
        
        # Plot Stem
        ax.stem(range(len(resid)), resid, linefmt='b-', markerfmt='bo', basefmt='r-')
        
        # Threshold (aprox 2 std)
        lim = 2 * np.std(resid)
        ax.axhline(lim, c='r', ls='--'); ax.axhline(-lim, c='r', ls='--')
        
        ax.set_title("Resíduos Padronizados (Outliers)")
        ax.set_xlabel("Índice"); ax.set_ylabel("Resíduo")
        self.fig.tight_layout()
        self.canvas.draw()

    def plot_resid_x(self):
        stats = self.controller.last_stats
        var = self.cb_x.get()
        df = stats.get('Dados_Utilizados') if stats else None
        
        if not stats or df is None or var not in df.columns: 
            return messagebox.showwarning("Aviso", "Variável não encontrada no modelo.")

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.scatter(df[var], stats['Residuos'], alpha=0.6)
        ax.axhline(0, c='r', ls='--')
        ax.set_title(f"Resíduos vs {var}")
        ax.set_xlabel(var); ax.set_ylabel("Erro")
        self.fig.tight_layout()
        self.canvas.draw()