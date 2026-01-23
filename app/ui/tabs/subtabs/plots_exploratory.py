import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import numpy as np

class ExploratoryPlotsSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Top Controls
        fr_top = ttk.Frame(self, padding=5)
        fr_top.pack(fill='x')
        
        ttk.Label(fr_top, text="Variável:").pack(side='left')
        self.cb_var = ttk.Combobox(fr_top, state="readonly", width=15)
        self.cb_var.pack(side='left', padx=5)
        
        ttk.Button(fr_top, text="Histograma & BoxPlot", command=self.plot_distribution).pack(side='left', padx=2)
        ttk.Button(fr_top, text="Matriz de Correlação", command=self.plot_correlation).pack(side='left', padx=2)
        
        # Right side buttons
        ttk.Button(fr_top, text="💾 Salvar", command=self.save_image).pack(side='right', padx=5)
        ttk.Button(fr_top, text="❓ Ajuda", command=self.show_help).pack(side='right')

        # Plot Area
        self.fig = plt.Figure(figsize=(6, 5), dpi=90)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def update_vars(self, cols):
        self.cb_var['values'] = cols
        if cols: self.cb_var.set(cols[0])

    def show_help(self):
        msg = (
            "GUIA DE INTERPRETAÇÃO:\n\n"
            "1. HISTOGRAMA (Gráfico de Barras):\n"
            "   - Objetivo: Ver a distribuição dos dados.\n"
            "   - Bom: Formato de 'Sino' (centro alto, bordas baixas).\n"
            "   - Ruim: Barras todas de um lado (Assimétrico). Tente Ln(x).\n\n"
            "2. BOXPLOT (Caixa com Bigodes):\n"
            "   - Objetivo: Encontrar Outliers.\n"
            "   - Pontos Pretos fora dos 'bigodes': São Outliers (Valores extremos).\n"
            "   - Linha no meio da caixa: Mediana.\n\n"
            "3. MATRIZ DE CORRELAÇÃO:\n"
            "   - Vermelho/Azul Forte: Variáveis muito ligadas.\n"
            "   - Cuidado se duas variáveis X forem muito parecidas (Multicolinearidade)."
        )
        messagebox.showinfo("Ajuda: Análise Exploratória", msg)

    def save_image(self):
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if f:
            try:
                self.fig.savefig(f, dpi=300)
                messagebox.showinfo("Sucesso", "Imagem salva!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def plot_distribution(self):
        df = self.controller.data_handler.get_data()
        col = self.cb_var.get()
        if df is None or col not in df.columns: return

        self.fig.clear()
        ax1 = self.fig.add_subplot(211)
        ax2 = self.fig.add_subplot(212)

        data = df[col].dropna()

        # Histogram
        ax1.hist(data, bins='auto', color='skyblue', edgecolor='black', alpha=0.7)
        ax1.set_title(f"Histograma: {col}")
        
        # BoxPlot
        ax2.boxplot(data, vert=False, patch_artist=True, boxprops=dict(facecolor="lightgreen"))
        ax2.set_title(f"BoxPlot: {col}")
        
        self.fig.tight_layout()
        self.canvas.draw()

    def plot_correlation(self):
        df = self.controller.data_handler.get_data()
        cols = self.controller.data_handler.get_numeric_columns()
        if df is None: return

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        corr = df[cols].corr()
        cax = ax.matshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
        self.fig.colorbar(cax)
        
        ticks = range(len(cols))
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(cols, rotation=45, ha="left", fontsize=8)
        ax.set_yticklabels(cols, fontsize=8)

        for i in range(len(cols)):
            for j in range(len(cols)):
                val = corr.iloc[i, j]
                color = "white" if abs(val) > 0.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=7)

        ax.set_title("Correlação")
        self.fig.tight_layout()
        self.canvas.draw()