import tkinter as tk
from tkinter import ttk
from app.ui.tabs.subtabs.optimizer_config import OptimizerConfigSubTab
from app.ui.tabs.subtabs.optimizer_results import OptimizerResultsSubTab

class OptimizerTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Notebook for Sub-tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # 1. Configuration Tab
        self.sub_config = OptimizerConfigSubTab(self.notebook, self.controller)
        self.notebook.add(self.sub_config, text="1. Configuração & Execução")

        # 2. Results Tab
        self.sub_results = OptimizerResultsSubTab(self.notebook, self.controller)
        self.notebook.add(self.sub_results, text="2. Resultados")

    # Property to allow Controller to access the results tree without changing code
    @property
    def tree_res(self):
        return self.sub_results.tree