import tkinter as tk
from tkinter import ttk

class ValidationScoring(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        
        lbl = ttk.Label(self, text="Pontuação da Fundamentação (Graus de Fundamentação)", font=("Segoe UI", 10, "bold"))
        lbl.pack(pady=10)

        # Main Table for Scoring Items
        cols = ("item", "pontos", "grau")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=6)
        
        self.tree.heading("item", text="Item da NBR")
        self.tree.heading("pontos", text="Pontos")
        self.tree.heading("grau", text="Classificação")
        
        self.tree.column("item", width=300)
        self.tree.column("pontos", width=80, anchor="center")
        self.tree.column("grau", width=120, anchor="center")
        
        self.tree.pack(fill="x", padx=10, pady=5)
        
        # Initialize rows
        self.items = [
            "Caracterização do Imóvel",
            "Quantidade Mínima de Dados",
            "Identificação dos Dados",
            "Extrapolação",
            "Significância das Variáveis",
            "Normalidade"
        ]
        
        for item in self.items:
            self.tree.insert("", "end", values=(item, "-", "-"))

        # Final Result
        self.lbl_final = ttk.Label(self, text="Grau Final: -", font=("Segoe UI", 12, "bold"))
        self.lbl_final.pack(pady=10)

    def update_score(self, stats):
        """
        Updates the scoring table based on the regression statistics.
        This contains the logic to determine Points (1, 2, 3) for each NBR criteria.
        """
        if not stats: return
        
        # Placeholder logic - ideally this comes from ValidatorEngine
        # For now, we simulate a basic check
        
        n_dados = stats.get('N_Amostras', 0)
        n_vars = stats.get('N_Variaveis', 0)
        
        # Example: Quantity of Data
        # Grau III: n >= 6(k+1) -> 3 points
        # Grau II: n >= 4(k+1) -> 2 points
        # Grau I: n >= 3(k+1) -> 1 point
        
        k = n_vars
        score_qty = 0
        grade_qty = "I"
        
        if n_dados >= 6 * (k + 1):
            score_qty = 3
            grade_qty = "III"
        elif n_dados >= 4 * (k + 1):
            score_qty = 2
            grade_qty = "II"
        elif n_dados >= 3 * (k + 1):
            score_qty = 1
            grade_qty = "I"
            
        # Update just this row for demo (Row Index 1)
        # In a real engine, we'd loop through all.
        items = self.tree.get_children()
        if len(items) > 1:
            self.tree.item(items[1], values=("Quantidade Mínima de Dados", score_qty, f"Grau {grade_qty}"))
            
        # Update Total (Simplified)
        self.lbl_final.config(text=f"Grau Final (Estimado): {grade_qty}")