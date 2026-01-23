import tkinter as tk
from tkinter import ttk

class ValidationScoringSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.combos = {}
        self._setup_ui()

    def _setup_ui(self):
        lbl = ttk.Label(self, text="Tabela de Pontuação - Grau de Fundamentação (NBR 14.653-2)", font=("Arial", 10, "bold"))
        lbl.pack(pady=10)

        fr_form = ttk.Frame(self)
        fr_form.pack(fill='x', padx=20)

        # Definition of items (Label, Options, Points)
        # Item 1: Characterization is binary in Table 1 for Urban Properties
        # Item 6: Precision will be auto-updated
        self.items = [
            ("1. Caracterização do Imóvel", ["Completa (3 pts)", "Simplificada (1 pt)"], [3, 1]),
            ("2. Quantidade de Dados (n)", ["Grau III (3 pts)", "Grau II (2 pts)", "Grau I (1 pt)"], [3, 2, 1]),
            ("3. Identificação dos Dados", ["Completa (3 pts)", "Apenas Fontes (2 pts)", "Restrita (1 pt)"], [3, 2, 1]),
            ("4. Extrapolação", ["Não admitida (3 pts)", "Admitida c/ Ajustes (2 pts)", "Admitida (1 pt)"], [3, 2, 1]),
            ("5. Tratamento dos Dados", ["Regressão Linear (3 pts)", "Fatores (2 pts)", "Outros (1 pt)"], [3, 2, 1]),
            ("6. Intervalo de Confiança", ["Amplitude <= 30% (3 pts)", "Amplitude <= 50% (2 pts)", "Amplitude > 50% (1 pt)"], [3, 2, 1])
        ]

        row = 0
        for label, options, scores in self.items:
            ttk.Label(fr_form, text=label).grid(row=row, column=0, sticky='w', pady=5)
            cb = ttk.Combobox(fr_form, values=options, state="readonly", width=35)
            cb.current(0) 
            cb.grid(row=row, column=1, padx=10, pady=5)
            self.combos[label] = {"cb": cb, "scores": scores}
            row += 1

        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=15)
        
        fr_res = ttk.Frame(self)
        fr_res.pack(fill='x', padx=20)
        
        ttk.Button(fr_res, text="Calcular Pontuação Final", command=self.calcular_grau).pack(side='left')
        self.lbl_result = ttk.Label(fr_res, text="Grau Atingido: ...", font=("Arial", 12, "bold"))
        self.lbl_result.pack(side='left', padx=20)

    def auto_fill_stats(self, stats):
        """Auto-selects Item 2 (Quantity) based on stats."""
        if not stats: return
        n = stats['N_Amostras']
        k = stats['N_Variaveis']
        g3_lim = 6 * (k + 1)
        g2_lim = 4 * (k + 1)
        
        cb = self.combos["2. Quantidade de Dados (n)"]["cb"]
        if n >= g3_lim: cb.current(0)
        elif n >= g2_lim: cb.current(1)
        else: cb.current(2)

    def auto_select_precision(self, amplitude_perc):
        """Auto-selects Item 6 (Precision) based on calculator."""
        cb = self.combos["6. Intervalo de Confiança"]["cb"]
        if amplitude_perc <= 30: cb.current(0)
        elif amplitude_perc <= 50: cb.current(1)
        else: cb.current(2)
        
        # Trigger recalculation visually
        self.calcular_grau()

    def calcular_grau(self):
        total = 0
        scores_list = []
        for label, data in self.combos.items():
            idx = data["cb"].current()
            pts = data["scores"][idx]
            total += pts
            scores_list.append(pts)

        # Pts Index: 0=Caract, 1=Quant, 2=Ident, 3=Extra, 4=Trat, 5=Interv
        pts_quant = scores_list[1]
        pts_extra = scores_list[3]
        pts_interv = scores_list[5]

        # NBR 14653-2 Table 1 Logic
        grau = "Reprovado"
        
        # Grau III requirements: Min 16 pts + Items (2, 4, 5, 6) must be Max Score
        if total >= 16 and pts_quant==3 and pts_extra==3 and pts_interv==3:
            grau = "Grau III"
        # Grau II requirements: Min 10 pts + Items (2, 4, 5, 6) must be >= 2 pts
        elif total >= 10 and pts_quant>=2 and pts_extra>=2 and pts_interv>=2:
            grau = "Grau II"
        # Grau I
        elif total >= 6:
            grau = "Grau I"

        color = "green" if "III" in grau else "#D4AC0D" if "II" in grau else "red"
        self.lbl_result.config(text=f"Pontos: {total} -> {grau}", foreground=color)