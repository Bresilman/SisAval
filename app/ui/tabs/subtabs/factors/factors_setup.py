import tkinter as tk
from tkinter import ttk

class FactorsSetupSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        fr = ttk.LabelFrame(self, text="Definição do Imóvel Paradigma (Avaliando)", padding=15)
        fr.pack(fill='x', padx=10, pady=10)

        grid_opts = {'padx': 5, 'pady': 5, 'sticky': 'w'}

        # Depth
        ttk.Label(fr, text="Profundidade Padrão (m):").grid(row=0, column=0, **grid_opts)
        self.ent_prof = ttk.Entry(fr)
        self.ent_prof.insert(0, "30.00")
        self.ent_prof.grid(row=0, column=1, **grid_opts)

        # Topography
        ttk.Label(fr, text="Topografia do Avaliando:").grid(row=1, column=0, **grid_opts)
        self.cb_topo = ttk.Combobox(fr, values=["Plano", "Aclive Leve", "Declive Leve"], state="readonly")
        self.cb_topo.set("Plano")
        self.cb_topo.grid(row=1, column=1, **grid_opts)

        # Info
        ttk.Label(fr, text="Nota: Os fatores das amostras serão calculados para trazer\ntodos os dados para esta configuração padrão.", foreground="gray").grid(row=2, column=0, columnspan=2, **grid_opts)

    def get_paradigm_data(self):
        try:
            return {
                "profundidade": float(self.ent_prof.get().replace(',', '.')),
                "topografia": self.cb_topo.get()
            }
        except:
            return {"profundidade": 30.0, "topografia": "Plano"}