import tkinter as tk
from tkinter import ttk

class DataModel(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Ferramentas de Tratamento e Limpeza (Em Breve)", font=("Segoe UI", 12)).pack(pady=20)
        
        # Placeholder for future features like "Drop NaN", "Fill Mean", etc.
        btn_frame = ttk.Frame(self)
        btn_frame.pack()
        ttk.Button(btn_frame, text="Remover Duplicatas").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Preencher Nulos (Média)").pack(side="left", padx=5)

    def refresh_view(self):
        pass