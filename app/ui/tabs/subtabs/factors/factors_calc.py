import tkinter as tk
from tkinter import ttk, messagebox
import statistics

class FactorsCalcSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Top Controls
        fr_top = ttk.Frame(self)
        fr_top.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(fr_top, text="➕ Adicionar Amostra", command=self._add_row).pack(side='left')
        ttk.Button(fr_top, text="🧮 Calcular Média Saneada", command=self._calculate).pack(side='left', padx=10)

        # Table
        # Columns: ID, Price, F_Offer, F_Location, F_Pattern, Homogenized
        self.cols = ("ID", "Valor Original", "F. Oferta", "F. Loc.", "F. Padrão", "Valor Homog.")
        self.tree = ttk.Treeview(self, columns=self.cols, show="headings", height=10)
        
        for c in self.cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor="center")
        
        self.tree.pack(fill='both', expand=True, padx=5)

        # Result Area
        fr_res = ttk.LabelFrame(self, text="Resultados", padding=10)
        fr_res.pack(fill='x', padx=5, pady=5)
        
        self.lbl_res = ttk.Label(fr_res, text="Média Homogeneizada: R$ 0,00", font=("Arial", 12, "bold"))
        self.lbl_res.pack()

    def _add_row(self):
        # Adds a dummy row for editing (In a real app, this would be a popup form)
        # ID, Price, Factors (1.0 default), Result
        self.tree.insert("", "end", values=("1", "1000.00", "0.90", "1.00", "1.00", "Waiting..."))

    def _calculate(self):
        # Simple calculation logic
        values = []
        for item in self.tree.get_children():
            row = self.tree.item(item)['values']
            try:
                price = float(row[1])
                f1 = float(row[2])
                f2 = float(row[3])
                f3 = float(row[4])
                
                homog = price * f1 * f2 * f3
                values.append(homog)
                
                # Update row
                self.tree.item(item, values=(row[0], row[1], row[2], row[3], row[4], f"{homog:.2f}"))
            except:
                pass
        
        if values:
            avg = statistics.mean(values)
            self.lbl_res.config(text=f"Média Homogeneizada: R$ {avg:,.2f}")