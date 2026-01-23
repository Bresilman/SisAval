import tkinter as tk
from tkinter import ttk, messagebox

class EvolConstructionsSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Input Form
        fr_form = ttk.LabelFrame(self, text="Adicionar Edificação Principal (Método CUB)", padding=10)
        fr_form.pack(fill='x', padx=5, pady=5)

        # Row 1
        ttk.Label(fr_form, text="Nome (ex: Casa):").grid(row=0, column=0, sticky='e')
        self.ent_nome = ttk.Entry(fr_form); self.ent_nome.grid(row=0, column=1, sticky='w')
        
        ttk.Label(fr_form, text="Área (m²):").grid(row=0, column=2, sticky='e')
        self.ent_area = ttk.Entry(fr_form, width=10); self.ent_area.grid(row=0, column=3, sticky='w')

        ttk.Label(fr_form, text="CUB (R$/m²):").grid(row=0, column=4, sticky='e')
        self.ent_cub = ttk.Entry(fr_form, width=10); self.ent_cub.grid(row=0, column=5, sticky='w')

        # Row 2
        ttk.Label(fr_form, text="BDI (%):").grid(row=1, column=0, sticky='e')
        self.ent_bdi = ttk.Entry(fr_form, width=10); self.ent_bdi.grid(row=1, column=1, sticky='w')
        self.ent_bdi.insert(0, "0") # Default BDI 0

        ttk.Label(fr_form, text="Idade Real:").grid(row=1, column=2, sticky='e')
        self.ent_idade = ttk.Entry(fr_form, width=10); self.ent_idade.grid(row=1, column=3, sticky='w')

        ttk.Label(fr_form, text="Vida Útil:").grid(row=1, column=4, sticky='e')
        self.ent_vida = ttk.Entry(fr_form, width=10); self.ent_vida.grid(row=1, column=5, sticky='w')
        self.ent_vida.insert(0, "60")

        # Row 3
        ttk.Label(fr_form, text="Estado:").grid(row=2, column=0, sticky='e')
        self.cb_estado = ttk.Combobox(fr_form, values=["Novo", "Bom", "Regular", "Reparos Simples", "Reparos Importantes", "Sem Valor"], state="readonly")
        self.cb_estado.set("Regular")
        self.cb_estado.grid(row=2, column=1, columnspan=2, sticky='ew')

        ttk.Button(fr_form, text="➕ Adicionar", command=self._add_item).grid(row=2, column=4, columnspan=2, pady=10)

        # Table
        cols = ("Nome", "Área", "CUB", "BDI", "Novo", "K (Deprec.)", "Atual")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=6)
        for c in cols: 
            self.tree.heading(c, text=c)
            self.tree.column(c, width=70, anchor="center")
        self.tree.column("Nome", width=120, anchor="w")
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)

        ttk.Button(self, text="❌ Remover Selecionado", command=self._remove_item).pack(anchor='e', padx=5)

    def _add_item(self):
        try:
            data = {
                "nome": self.ent_nome.get(),
                "area": float(self.ent_area.get().replace(',', '.')),
                "cub": float(self.ent_cub.get().replace(',', '.')),
                "bdi": float(self.ent_bdi.get().replace(',', '.')),
                "idade": float(self.ent_idade.get()),
                "vida": float(self.ent_vida.get()),
                "estado": self.cb_estado.get()
            }
            self.controller.acao_add_principal(data)
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores numéricos.")

    def _remove_item(self):
        sel = self.tree.selection()
        if sel: self.tree.delete(sel)