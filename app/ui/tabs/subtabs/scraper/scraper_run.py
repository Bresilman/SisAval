import tkinter as tk
from tkinter import ttk

class ScraperRunSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Top Controls
        fr_top = ttk.Frame(self, padding=10)
        fr_top.pack(fill='x')

        ttk.Label(fr_top, text="1. Selecione a pasta com os arquivos HTML salvos:").pack(side='left')
        ttk.Button(fr_top, text="📂 Selecionar Pasta e Processar", command=self.controller.acao_importar_pasta).pack(side='left', padx=10)
        
        # Actions
        fr_act = ttk.LabelFrame(self, text="Ações sobre os dados encontrados", padding=5)
        fr_act.pack(fill='x', padx=10)
        
        ttk.Button(fr_act, text="⬇️ Enviar Selecionados para Aba Dados", command=self.controller.acao_enviar_para_analise).pack(side='right')
        ttk.Button(fr_act, text="❌ Descartar Selecionados", command=self._delete_selected).pack(side='right', padx=10)

        # Table
        self.tree = ttk.Treeview(self, show='headings', selectmode="extended")
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbar
        sb = ttk.Scrollbar(self, command=self.tree.yview)
        sb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=sb.set)

    def update_table(self, df):
        self.tree.delete(*self.tree.get_children())
        if df.empty: return
        
        # Set columns dynamically
        cols = list(df.columns)
        self.tree["columns"] = cols
        
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
            
        for idx, row in df.iterrows():
            # Store index in iid to track
            self.tree.insert("", "end", iid=idx, values=list(row))

    def _delete_selected(self):
        for item in self.tree.selection():
            self.tree.delete(item)