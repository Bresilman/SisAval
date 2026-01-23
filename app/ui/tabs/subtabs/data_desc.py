import tkinter as tk
from tkinter import ttk

class DataDescSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        cols = ("Variável", "N (Contagem)", "Média", "Desvio Padrão", "Mínimo", "Máximo", "CV (%)")
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        
        for c in cols:
            self.tree.heading(c, text=c)
            width = 100 if c != "Variável" else 150
            self.tree.column(c, width=width, anchor='center')
            
        self.tree.pack(fill='both', expand=True, side='left')
        
        sb = ttk.Scrollbar(self, command=self.tree.yview)
        sb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=sb.set)

    def calculate_desc(self, df, numeric_cols):
        self.tree.delete(*self.tree.get_children())
        for c in numeric_cols:
            try:
                s = df[c]
                count = s.count()
                mean = s.mean()
                std = s.std()
                min_v = s.min()
                max_v = s.max()
                cv = (std / mean * 100) if mean != 0 else 0
                
                vals = (
                    c, 
                    int(count), 
                    f"{mean:.2f}", 
                    f"{std:.2f}", 
                    f"{min_v:.2f}", 
                    f"{max_v:.2f}", 
                    f"{cv:.2f}%"
                )
                self.tree.insert("", "end", values=vals)
            except:
                pass