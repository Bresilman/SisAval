import tkinter as tk
from tkinter import ttk, Menu

class DataTableSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', pady=2)
        ttk.Label(toolbar, text="Visualização dos dados brutos carregados.", foreground="gray").pack(side='left')
        ttk.Button(toolbar, text="❌ Excluir Linha Selecionada", command=self.controller.acao_excluir_dado).pack(side='right')
        
        # Treeview Principal
        self.tree = ttk.Treeview(self, show='headings')
        self.tree.pack(fill='both', expand=True, side='left')
        
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=sb.set)

        # Menu de Contexto
        self.menu_ctx = Menu(self, tearoff=0)
        self.menu_ctx.add_command(label="Excluir Linha", command=self.controller.acao_excluir_dado)
        self.tree.bind("<Button-3>", lambda e: self.menu_ctx.post(e.x_root, e.y_root))

    def update_data(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        for c in df.columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=90)
        
        for i, row in df.iterrows():
            self.tree.insert("", "end", iid=i, values=list(row))