import tkinter as tk
from tkinter import ttk

class ReportConfigSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # 1. Client Info
        fr_client = ttk.LabelFrame(self, text="Dados do Trabalho", padding=10)
        fr_client.pack(fill='x', pady=5)

        ttk.Label(fr_client, text="Cliente / Solicitante:").pack(anchor='w')
        self.ent_client = ttk.Entry(fr_client)
        self.ent_client.pack(fill='x', pady=2)

        ttk.Label(fr_client, text="Finalidade (ex: Venda, Garantia):").pack(anchor='w')
        self.ent_finality = ttk.Entry(fr_client)
        self.ent_finality.insert(0, "Determinação do Valor de Mercado para Fins de Venda")
        self.ent_finality.pack(fill='x', pady=2)

        # 2. Market Diagnosis (Multiline Text)
        fr_diag = ttk.LabelFrame(self, text="Diagnóstico de Mercado (Texto Livre)", padding=10)
        fr_diag.pack(fill='both', expand=True, pady=5)

        ttk.Label(fr_diag, text="Descreva liquidez, oferta e tendências:").pack(anchor='w')
        self.txt_diag = tk.Text(fr_diag, height=10, font=("Arial", 10))
        self.txt_diag.pack(fill='both', expand=True)
        
        # Default Text
        default_text = (
            "O mercado imobiliário na região apresenta liquidez moderada. "
            "Observa-se equilíbrio entre oferta e demanda para a tipologia avaliada. "
            "A infraestrutura urbana é completa, contando com saneamento, energia e transporte."
        )
        self.txt_diag.insert("1.0", default_text)

    def get_data(self):
        return {
            "cliente": self.ent_client.get(),
            "finalidade": self.ent_finality.get(),
            "diagnostico": self.txt_diag.get("1.0", "end-1c")
        }