import tkinter as tk
from tkinter import ttk

# FIX: Correct imports pointing to the actual filenames and class names (PascalCase)
from app.ui.tabs.subtabs.validation_checklist import ValidationChecklist
from app.ui.tabs.subtabs.validation_precision import ValidationPrecision
from app.ui.tabs.subtabs.validation_scoring import ValidationScoring

class ValidationTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Initialize subtabs with controller
        self.sub_checklist = ValidationChecklist(self.notebook, self.controller)
        self.sub_precision = ValidationPrecision(self.notebook, self.controller)
        self.sub_scoring = ValidationScoring(self.notebook, self.controller)

        # Add to notebook
        self.notebook.add(self.sub_checklist, text="Checklist NBR")
        self.notebook.add(self.sub_precision, text="Precisão e Intervalo")
        self.notebook.add(self.sub_scoring, text="Pontuação e Graus")

    def update_all(self, stats, report):
        """Called by StatsController after regression"""
        if hasattr(self.sub_checklist, 'update_status'):
            self.sub_checklist.update_status(report)
        
        if hasattr(self.sub_precision, 'update_precision'):
            self.sub_precision.update_precision(stats)
            
        if hasattr(self.sub_scoring, 'update_score'):
            self.sub_scoring.update_score(stats)