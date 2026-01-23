import tkinter as tk
from tkinter import ttk, messagebox

class EvolComplementarySubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        fr_form = ttk.LabelFrame(self, text="Adicionar Obras Complementares (Muro, Piscina, Pavimentação)", padding=10)
        fr_form.pack(fill='x', padx=5, pady=5)

        # Simple inputs
        ttk.Label(fr_form, text="Descrição:").grid(row=0, column=0)
        self.ent_desc = ttk.Entry(fr_form, width=25)
        self.ent_desc.grid(row=0, column=1)

        ttk.Label(fr_form, text="Valor Total Estimado (R$):").grid(row=0, column=2)
        self.ent_val = ttk.Entry(fr_form, width=15)
        self.ent_val.grid(row=0, column=3)

        ttk.Label(fr_form, text="(Já depreciado)", font=("Arial", 8), foreground="gray").grid(row=1, column=3)

        ttk.Button(fr_form, text="➕ Adicionar", command=self._add).grid(row=0, column=4, padx=10)

        # Table
        self.tree = ttk.Treeview(self, columns=("Desc", "Valor"), show="headings", height=5)
        self.tree.heading("Desc", text="Descrição")
        self.tree.heading("Valor", text="Valor Atual (Depreciado)")
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        ttk.Button(self, text="❌ Remover", command=lambda: [self.tree.delete(i) for i in self.tree.selection()]).pack(anchor='e', padx=5)

    def _add(self):
        try:
            desc = self.ent_desc.get()
            val = float(self.ent_val.get().replace(',', '.'))
            self.tree.insert("", "end", values=(desc, f"R$ {val:,.2f}"))
        except:
            messagebox.showerror("Erro", "Valor inválido")