import tkinter as tk
from tkinter import ttk

class OptimizerResultsSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        fr_main = ttk.Frame(self, padding=10)
        fr_main.pack(fill='both', expand=True)

        lbl = ttk.Label(fr_main, text="Ranking de Modelos (Linear vs Log-Log):", font=("Arial", 10, "bold"))
        lbl.pack(anchor='w', pady=(0,5))

        # Table with 'Modelo' column
        cols = ("Modelo", "Vars", "R2", "Status")
        self.tree = ttk.Treeview(fr_main, columns=cols, show="headings")
        
        self.tree.heading("Modelo", text="Transformação")
        self.tree.heading("Vars", text="Variáveis Utilizadas")
        self.tree.heading("R2", text="R² Ajustado")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("Modelo", width=80, anchor="center")
        self.tree.column("Vars", width=400)
        self.tree.column("R2", width=80, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        
        self.tree.pack(fill='both', expand=True, side='left')
        
        sb = ttk.Scrollbar(fr_main, orient="vertical", command=self.tree.yview)
        sb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=sb.set)
        
        ttk.Button(self, text="Carregar Modelo Selecionado", command=self._load_model).pack(pady=10, padx=10, anchor='e')

    def _load_model(self):
        sel = self.tree.selection()
        if sel:
            idx = int(sel[0])
            self.controller.acao_carregar_modelo_otimizado(idx)