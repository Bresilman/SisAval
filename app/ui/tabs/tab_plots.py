import tkinter as tk
from tkinter import ttk
from app.ui.tabs.subtabs.plots_exploratory import ExploratoryPlotsSubTab
from app.ui.tabs.subtabs.plots_diagnostic import DiagnosticPlotsSubTab
from app.ui.tabs.subtabs.plots_scenarios import ScenariosPlotsSubTab

class PlotsTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Create Notebook for Sub-tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # 1. Exploratory (Data Analysis)
        self.sub_exploratory = ExploratoryPlotsSubTab(self.notebook, self.controller)
        self.notebook.add(self.sub_exploratory, text="1. Análise Exploratória (Dados)")

        # 2. Diagnostic (Model Check)
        self.sub_diagnostic = DiagnosticPlotsSubTab(self.notebook, self.controller)
        self.notebook.add(self.sub_diagnostic, text="2. Diagnóstico do Modelo")

        # 3. Scenarios (Sensitivity)
        self.sub_scenarios = ScenariosPlotsSubTab(self.notebook, self.controller)
        self.notebook.add(self.sub_scenarios, text="3. Cenários e Sensibilidade")

    def atualizar_variaveis(self, colunas):
        """Called by controller after loading data/calculating."""
        # Distribute variable list to sub-tabs
        self.sub_exploratory.update_vars(colunas)
        
        # Diagnostic and Scenarios usually need X columns specifically, 
        # but passing all numerical cols is safe for selection.
        self.sub_diagnostic.update_vars(colunas)
        self.sub_scenarios.update_vars(colunas)