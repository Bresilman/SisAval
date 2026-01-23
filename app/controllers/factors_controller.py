from tkinter import messagebox
from app.engines.factors_engine import FactorsEngine

class FactorsController:
    def __init__(self, main_controller):
        self.main = main_controller
        self.engine = FactorsEngine()
        self.view = self.main.view

    def calcular_fatores(self):
        try:
            # 1. Get Subject Data
            paradigma = self.view.tab_factors.sub_setup.get_paradigm_data()
            
            # 2. Get Samples from Grid
            tree = self.view.tab_factors.sub_grid.tree
            items = tree.get_children()
            
            amostras = []
            for item in items:
                vals = tree.item(item)['values']
                # Reconstruct raw data from tree columns
                # ID(0), Unit(1), OfferType(2), Prof(3), Topo(4), Local(5)
                # Note: We need Price/Area to be precise, but Unit is enough for engine logic
                # Let's approximate Price = Unit * 1
                
                amostras.append({
                    "id": vals[0],
                    "preco": float(vals[1]), # Treating Unit as Price for simplicity in this MVP
                    "area": 1.0,
                    "tipo_valor": vals[2],
                    "profundidade": vals[3],
                    "topografia": vals[4],
                    "fator_local": vals[5]
                })

            if not amostras: return

            # 3. Calculate Homogenization
            results = self.engine.calcular_homogeneizacao(amostras, paradigma)
            
            # 4. Update Grid with Factors
            homog_values = []
            for i, res in enumerate(results):
                item_id = items[i]
                f = res['fatores']
                
                # Update visual columns with calculated factors
                # ID, UnitOrig, F.Of, F.Pr, F.To, F.Lo, UnitHomog
                tree.item(item_id, values=(
                    res['id'],
                    f"{res['vu_original']:.2f}",
                    f"{f['oferta']:.2f}",
                    f"{f['prof']:.2f}",
                    f"{f['topo']:.2f}",
                    f"{f['local']:.2f}",
                    f"{res['vu_homogeneizado']:.2f}"
                ))
                homog_values.append(res['vu_homogeneizado'])

            # 5. Statistics
            stats = self.engine.calcular_estatisticas(homog_values)
            if stats:
                lbl = self.view.tab_factors.sub_grid.lbl_stats
                lbl.config(text=f"Média: R$ {stats['media']:,.2f} | CV: {stats['cv']:.2f}% | IC: {stats['ic_min']:,.2f} a {stats['ic_max']:,.2f}")
                
                # Highlight Outliers
                for i in stats['outliers_idx']:
                    # TODO: Add red tag to row
                    pass

        except Exception as e:
            messagebox.showerror("Erro", str(e))