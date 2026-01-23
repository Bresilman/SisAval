import tkinter as tk
from tkinter import ttk, messagebox

class FactorsGridSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # 1. Inputs Row
        fr_inp = ttk.LabelFrame(self, text="Inserir Amostra", padding=5)
        fr_inp.pack(fill='x', padx=5, pady=5)

        self.vars = {}
        fields = [
            ("Preço (R$):", 10), ("Área (m²):", 8), 
            ("Profund. (m):", 8), ("F. Local:", 6)
        ]
        
        col = 0
        for lbl, width in fields:
            ttk.Label(fr_inp, text=lbl).grid(row=0, column=col, padx=2)
            ent = ttk.Entry(fr_inp, width=width)
            ent.grid(row=0, column=col+1, padx=2)
            self.vars[lbl] = ent
            col += 2

        # Combos
        ttk.Label(fr_inp, text="Oferta?").grid(row=0, column=col)
        self.cb_oferta = ttk.Combobox(fr_inp, values=["Oferta", "Vendido"], width=8, state="readonly")
        self.cb_oferta.set("Oferta")
        self.cb_oferta.grid(row=0, column=col+1)

        ttk.Label(fr_inp, text="Topografia:").grid(row=0, column=col+2)
        self.cb_topo = ttk.Combobox(fr_inp, values=["Plano", "Aclive Leve", "Aclive Acentuado", "Declive Leve"], width=10)
        self.cb_topo.set("Plano")
        self.cb_topo.grid(row=0, column=col+3)

        ttk.Button(fr_inp, text="➕", command=self._add).grid(row=0, column=col+4, padx=10)

        # 2. Table
        cols = ("ID", "Unit. Orig", "F.Oferta", "F.Prof", "F.Topo", "F.Local", "Unit. Homog")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=80, anchor="center")
        
        self.tree.pack(fill='both', expand=True, padx=5)

        # 3. Results Footer
        fr_res = ttk.Frame(self, padding=10, relief="groove")
        fr_res.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(fr_res, text="▶ CALCULAR RESULTADOS", command=self.controller.acao_calcular_fatores).pack(side='left')
        
        self.lbl_stats = ttk.Label(fr_res, text="Média: R$ 0,00 | CV: 0.00% | Intervalo: ...", font=("Arial", 10, "bold"))
        self.lbl_stats.pack(side='right')

    def _add(self):
        try:
            # Basic validation
            p = float(self.vars["Preço (R$):"].get())
            a = float(self.vars["Área (m²):"].get())
            prof = float(self.vars["Profund. (m):"].get())
            fl = float(self.vars["F. Local:"].get())
            
            # Insert raw data (factors calculated later)
            item_id = len(self.tree.get_children()) + 1
            unit = p/a
            
            # Format: ID, Unit Orig, Type, Prof, Topo, Local, Hidden(Price, Area)
            self.tree.insert("", "end", values=(
                item_id, f"{unit:.2f}", 
                self.cb_oferta.get(), 
                prof, 
                self.cb_topo.get(), 
                fl, 
                "..."
            ), tags=("row",))
            
            # Store raw data in a hidden property or use the tree values
            # For simplicity, we parse tree values in controller
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos")