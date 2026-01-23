import tkinter as tk
from tkinter import ttk

class DataModelSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Layout Split (2 Columns)
        paned = ttk.PanedWindow(self, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=10, pady=10)

        # Column 1: Y Variable
        fr_y = ttk.LabelFrame(paned, text="Variável Dependente (Y)", padding=15)
        paned.add(fr_y, weight=1)
        
        ttk.Label(fr_y, text="Variável alvo da avaliação:", foreground="blue").pack(anchor='w', pady=(0, 5))
        self.combo_y = ttk.Combobox(fr_y, state="readonly", font=("Arial", 10))
        self.combo_y.pack(fill='x', pady=5)
        ttk.Label(fr_y, text="Ex: 'Valor Unitário' ou 'Valor Total'", foreground="gray").pack(anchor='w')

        # Column 2: X Variables
        fr_x = ttk.LabelFrame(paned, text="Variáveis Independentes (X)", padding=15)
        paned.add(fr_x, weight=3)
        
        ttk.Label(fr_x, text="Selecione as variáveis explicativas:", foreground="blue").pack(anchor='w', pady=(0, 5))
        
        fr_list = ttk.Frame(fr_x)
        fr_list.pack(fill='both', expand=True, pady=5)
        
        self.listbox_x = tk.Listbox(fr_list, selectmode='multiple', activestyle='dotbox', font=("Arial", 10))
        self.listbox_x.pack(side='left', fill='both', expand=True)
        
        sb_x = ttk.Scrollbar(fr_list, command=self.listbox_x.yview)
        sb_x.pack(side='right', fill='y')
        self.listbox_x.configure(yscrollcommand=sb_x.set)
        
        ttk.Label(fr_x, text="Segure Ctrl para selecionar múltiplas variáveis.", foreground="gray").pack(anchor='w')

    def update_selectors(self, numeric_cols):
        sel_indices = self.listbox_x.curselection()
        sel_values = [self.listbox_x.get(i) for i in sel_indices]
        
        self.combo_y['values'] = numeric_cols
        self.listbox_x.delete(0, 'end')
        
        for c in numeric_cols:
            self.listbox_x.insert('end', c)
            if c in sel_values:
                self.listbox_x.selection_set('end')