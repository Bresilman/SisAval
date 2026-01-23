import tkinter as tk
from tkinter import ttk

class EvolSummarySubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # 1. Land Inputs
        fr_land = ttk.LabelFrame(self, text="1. Valor do Terreno & Fator de Comercialização", padding=10)
        fr_land.pack(fill='x', padx=5, pady=5)

        ttk.Label(fr_land, text="Valor do Terreno (R$):").grid(row=0, column=0, sticky='e')
        self.ent_terr = ttk.Entry(fr_land)
        self.ent_terr.grid(row=0, column=1, padx=5)
        self.ent_terr.insert(0, "0.00")

        ttk.Button(fr_land, text="Importar da Regressão", command=self._import_land).grid(row=0, column=2, padx=5)

        ttk.Label(fr_land, text="Fator Comercialização (FC):").grid(row=1, column=0, sticky='e', pady=5)
        self.ent_fc = ttk.Entry(fr_land)
        self.ent_fc.grid(row=1, column=1, padx=5)
        self.ent_fc.insert(0, "1.00")

        # 2. Results
        fr_res = ttk.LabelFrame(self, text="Resumo do Método Evolutivo", padding=15)
        fr_res.pack(fill='both', expand=True, padx=5, pady=10)

        # Grid of labels
        self.lbls = {}
        rows = [
            ("Valor do Terreno (VT):", "vt"),
            ("Benfeitorias Principais:", "bp"),
            ("Obras Complementares:", "oc"),
            ("Soma (VT + Benf):", "soma"),
            ("Valor de Mercado Final (x FC):", "final")
        ]
        
        for i, (txt, key) in enumerate(rows):
            font = ("Arial", 12, "bold") if key == "final" else ("Arial", 10)
            ttk.Label(fr_res, text=txt, font=font).grid(row=i, column=0, sticky='e', pady=5)
            lbl = ttk.Label(fr_res, text="R$ 0,00", font=font, foreground="blue" if key=="final" else "black")
            lbl.grid(row=i, column=1, sticky='w', padx=20)
            self.lbls[key] = lbl

        ttk.Button(fr_res, text="CALCULAR TOTAL", command=self.controller.acao_calcular_total_evolutivo).grid(row=len(rows), column=0, columnspan=2, pady=20)

    def _import_land(self):
        # Try to get value from Calculator result
        try:
            # Assuming calculator stores result in label text.
            # Ideally, get from controller variable.
            # Using controller.last_stats logic if available
            if self.controller.last_stats:
                # We need the calculated value from calculator, not just stats.
                # Let's try to parse the calculator label directly for quick integration
                txt = self.controller.view.tab_calculator.lbl_total.cget("text")
                val = txt.replace("R$", "").replace(".", "").replace(",", ".").strip()
                if float(val) > 0:
                    self.ent_terr.delete(0, tk.END)
                    self.ent_terr.insert(0, val)
        except:
            pass