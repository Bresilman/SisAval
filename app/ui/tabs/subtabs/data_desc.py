import tkinter as tk
from tkinter import ttk

class DataDesc(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.txt_stats = tk.Text(self, font=("Consolas", 10))
        self.txt_stats.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def refresh_view(self):
        dh = getattr(self.controller, 'data_handler', None)
        if not dh: return
        
        df = dh.get_data()
        if df is None: return
        
        # Calculate describe
        try:
            desc = df.describe().to_string()
            self.txt_stats.delete(1.0, tk.END)
            self.txt_stats.insert(tk.END, desc)
        except:
            self.txt_stats.insert(tk.END, "Não foi possível calcular estatísticas (verifique dados numéricos).")