import tkinter as tk
from tkinter import ttk
from app.ui.tabs.subtabs.factors.factors_setup import FactorsSetupSubTab
from app.ui.tabs.subtabs.factors.factors_grid import FactorsGridSubTab

class FactorsTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=5, pady=5)

        self.sub_setup = FactorsSetupSubTab(nb)
        nb.add(self.sub_setup, text="1. Paradigma (Referência)")

        self.sub_grid = FactorsGridSubTab(nb, self.controller)
        nb.add(self.sub_grid, text="2. Cálculo de Fatores")