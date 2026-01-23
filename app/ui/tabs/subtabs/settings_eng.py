import tkinter as tk
from tkinter import ttk

class SettingsEngSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.table_data = [
            ("Residencial Casa", 60),
            ("Residencial Apartamento", 60),
            ("Galpão Alvenaria", 40),
            ("Galpão Metálico", 40),
            ("Loja Comercial", 60),
            ("Escritório", 60),
            ("Industrial", 40)
        ]
        self._setup_ui()

    def _setup_ui(self):
        fr_main = ttk.Frame(self, padding=20)
        fr_main.pack(fill='both', expand=True)

        # 1. Depreciation Parameters
        fr_dep = ttk.LabelFrame(fr_main, text="Parâmetros de Depreciação (Ross-Heidecke)", padding=15)
        fr_dep.pack(fill='x', pady=10)

        ttk.Label(fr_dep, text="Valor Residual Mínimo (Sucata):").pack(side='left')
        self.sp_kmin = ttk.Spinbox(fr_dep, from_=0.0, to=0.5, increment=0.05, width=8)
        self.sp_kmin.set(0.20)
        self.sp_kmin.pack(side='left', padx=10)
        ttk.Label(fr_dep, text="(Padrão: 0.20)").pack(side='left', padx=5)

        # 2. Life Span Table (Editable)
        fr_table = ttk.LabelFrame(fr_main, text="Tabela de Vida Útil (Anos)", padding=10)
        fr_table.pack(fill='both', expand=True, pady=10)

        # List/Editor
        fr_edit = ttk.Frame(fr_table)
        fr_edit.pack(fill='x', pady=5)
        
        ttk.Label(fr_edit, text="Tipo:").pack(side='left')
        self.ent_type = ttk.Entry(fr_edit, width=20)
        self.ent_type.pack(side='left', padx=5)
        
        ttk.Label(fr_edit, text="Anos:").pack(side='left')
        self.ent_years = ttk.Entry(fr_edit, width=8)
        self.ent_years.pack(side='left', padx=5)
        
        ttk.Button(fr_edit, text="Atualizar/Adicionar", command=self._upsert_item).pack(side='left', padx=10)

        # Treeview
        self.tree = ttk.Treeview(fr_table, columns=("Tipo", "Anos"), show="headings", height=8)
        self.tree.heading("Tipo", text="Tipologia")
        self.tree.heading("Anos", text="Vida Útil (Anos)")
        self.tree.column("Tipo", width=200)
        self.tree.column("Anos", width=100, anchor="center")
        self.tree.pack(fill='both', expand=True)
        
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        
        # Populate initial data
        self._refresh_tree()

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for k, v in self.table_data:
            self.tree.insert("", "end", values=(k, v))

    def _on_select(self, event):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0])['values']
            self.ent_type.delete(0, tk.END); self.ent_type.insert(0, vals[0])
            self.ent_years.delete(0, tk.END); self.ent_years.insert(0, vals[1])

    def _upsert_item(self):
        t = self.ent_type.get()
        y = self.ent_years.get()
        if t and y:
            # Update local data list logic (simple)
            found = False
            for i, (k, v) in enumerate(self.table_data):
                if k == t:
                    self.table_data[i] = (k, y)
                    found = True
                    break
            if not found:
                self.table_data.append((t, y))
            
            self._refresh_tree()

    def get_data(self):
        # Return dict of settings
        return {
            "k_min": float(self.sp_kmin.get()),
            "vida_util_table": dict(self.table_data)
        }