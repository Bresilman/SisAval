import tkinter as tk
from tkinter import ttk

# Import the new modular sub-tabs
# Ensure you created the __init__.py in the 'subtabs' folder for this to work perfectly
from app.ui.tabs.subtabs.regression_summary import RegressionSummarySubTab
from app.ui.tabs.subtabs.regression_residuals import RegressionResidualsSubTab
from app.ui.tabs.subtabs.regression_plots import RegressionPlotsSubTab
from app.ui.tabs.subtabs.regression_correlation import RegressionCorrelationSubTab

class RegressionTab(ttk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent)
        self.controller = ctrl
        self._setup_ui()

    def _setup_ui(self):
        # Top Panel (Buttons and Label)
        top = ttk.Frame(self)
        top.pack(fill='x', pady=5, padx=5)
        ttk.Button(top, text="📄 Exportar Laudo", command=self.controller.acao_gerar_relatorio).pack(side='right')
        ttk.Label(top, text="Resultados da Regressão", font=("Arial", 10, "bold")).pack(side='left')

        # Internal Notebook
        self.nb_res = ttk.Notebook(self)
        self.nb_res.pack(fill='both', expand=True)

        # 1. Summary
        self.subtab_summary = RegressionSummarySubTab(self.nb_res)
        self.nb_res.add(self.subtab_summary, text="Resumo Estatístico")

        # 2. Residuals Table
        self.subtab_residuals = RegressionResidualsSubTab(self.nb_res)
        self.nb_res.add(self.subtab_residuals, text="Tabela de Resíduos")

        # 3. Graphs
        self.subtab_plots = RegressionPlotsSubTab(self.nb_res)
        self.nb_res.add(self.subtab_plots, text="Gráficos Diagnósticos")

        # 4. Correlation Matrix
        self.subtab_corr = RegressionCorrelationSubTab(self.nb_res)
        self.nb_res.add(self.subtab_corr, text="Matriz de Correlação")

    def update_results(self, text, stats_data):
        """Distributes the data to the appropriate sub-tab."""
        # CHANGED: Use the new method to populate the dashboard
        self.subtab_summary.update_summary_from_stats(stats_data)
        
        # 2. Update Residuals Table
        self.subtab_residuals.update_table(stats_data)

        # 3. Update Plots
        self.subtab_plots.update_plots(stats_data)

        # 4. Update Correlation Matrix
        self.subtab_corr.update_corr(stats_data.get('Dados_Utilizados'))