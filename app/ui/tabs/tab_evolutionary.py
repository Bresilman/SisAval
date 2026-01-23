import tkinter as tk
from tkinter import ttk
from app.ui.tabs.subtabs.evol_constructions import EvolConstructionsSubTab
from app.ui.tabs.subtabs.evol_complementary import EvolComplementarySubTab
from app.ui.tabs.subtabs.evol_summary import EvolSummarySubTab

class EvolutionaryTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: Constructions
        self.sub_const = EvolConstructionsSubTab(self.notebook, self.controller)
        self.notebook.add(self.sub_const, text="1. Edificações")

        # Tab 2: Complementary
        self.sub_comp = EvolComplementarySubTab(self.notebook, self.controller)
        self.notebook.add(self.sub_comp, text="2. Obras Complementares")

        # Tab 3: Summary
        self.sub_sum = EvolSummarySubTab(self.notebook, self.controller)
        self.notebook.add(self.sub_sum, text="3. Fechamento do Laudo")