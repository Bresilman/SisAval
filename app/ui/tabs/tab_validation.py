import tkinter as tk
from tkinter import ttk
from app.ui.tabs.subtabs.validation_checklist import ValidationChecklistSubTab
from app.ui.tabs.subtabs.validation_scoring import ValidationScoringSubTab
from app.ui.tabs.subtabs.validation_precision import ValidationPrecisionSubTab

class ValidationTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # Notebook for Sub-tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # 1. Checklist
        self.sub_checklist = ValidationChecklistSubTab(self.notebook)
        self.notebook.add(self.sub_checklist, text="✅ Checklist Estatístico")

        # 2. Scoring (Enquadramento)
        self.sub_scoring = ValidationScoringSubTab(self.notebook)
        self.notebook.add(self.sub_scoring, text="🏆 Enquadramento (Graus)")

        # 3. Precision (Fronteiras)
        self.sub_precision = ValidationPrecisionSubTab(self.notebook)
        self.notebook.add(self.sub_precision, text="🎯 Precisão & Fronteiras")

    def update_all(self, stats, validator_report):
        """Updates all sub-tabs at once."""
        # 1. Checklist
        self.sub_checklist.update_data(validator_report)
        
        # 2. Scoring (Auto-fill stats based items)
        self.sub_scoring.auto_fill_stats(stats)
        
        # 3. Precision (Boundaries)
        self.sub_precision.update_boundaries(stats.get('Dados_Utilizados'))