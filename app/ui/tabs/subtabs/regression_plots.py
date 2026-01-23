import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from app.ui.plots import PlotManager

class RegressionPlotsSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # Split: Plots on Top, Guide on Bottom
        paned = ttk.PanedWindow(self, orient="vertical")
        paned.pack(fill='both', expand=True)

        # Plots Area
        fr_plots = ttk.Frame(paned)
        paned.add(fr_plots, weight=4)
        self.plot_manager = PlotManager(fr_plots)

        # Bottom Area
        fr_bottom = ttk.LabelFrame(paned, text="Análise Visual dos Gráficos", padding=10)
        paned.add(fr_bottom, weight=1)

        # Save Button
        ttk.Button(fr_bottom, text="📷 Salvar Imagem", command=self.salvar_imagem).pack(side='right', anchor='n')

        # Guide Text
        txt_guide = (
            "1. ADERÊNCIA (Sup. Esq): Pontos devem estar próximos à linha tracejada.\n"
            "2. HISTOGRAMA (Sup. Dir): Deve parecer um 'sino' (distribuição normal). Se estiver torto, tente Ln(x).\n"
            "3. HOMOCEDASTICIDADE (Inf. Esq): Pontos devem estar espalhados aleatoriamente (nuvem).\n"
            "   ⚠️ PERIGO: Se formar um 'Funil' (<) ou 'Cone', o modelo é inválido (Heterocedasticidade).\n"
            "4. QQ-PLOT (Inf. Dir): Pontos devem seguir a linha reta diagonal."
        )
        lbl = tk.Label(fr_bottom, text=txt_guide, justify="left", anchor="w", font=("Arial", 9), bg="#f0f0f0", relief="sunken", padx=10, pady=5)
        lbl.pack(side='left', fill='both', expand=True)

    def update_plots(self, stats):
        self.plot_manager.plotar_diagnostico(
            stats['Observado'], 
            stats['Valores_Previstos'], 
            stats['Residuos']
        )

    def salvar_imagem(self):
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPG", "*.jpg")])
        if f:
            try:
                self.plot_manager.figure.savefig(f, dpi=300)
                messagebox.showinfo("Sucesso", "Gráfico salvo em alta resolução!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))