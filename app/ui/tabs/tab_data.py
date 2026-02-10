import tkinter as tk
from tkinter import ttk
from app.controllers.data_controller import DataController

# Import Subtabs
from app.ui.tabs.subtabs.data_tools import DataTools
from app.ui.tabs.subtabs.data_table import DataTable
from app.ui.tabs.subtabs.data_variables import DataVariables
from app.ui.tabs.subtabs.data_desc import DataDesc
from app.ui.tabs.subtabs.data_model import DataModel

class TabData(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Ensure DataController exists
        if not hasattr(self.controller, 'data_handler'):
            self.data_ctrl = DataController(self.controller)
            self.controller.data_handler = self.data_ctrl
        else:
            self.data_ctrl = self.controller.data_handler
            
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # 1. GLOBAL TOOLS (Top Bar)
        # Keeps file operations always visible
        self.tools = DataTools(self, self.controller)
        self.tools.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # 2. SUBTABS NOTEBOOK (Content Area)
        # This fixes the "can't see subtabs" issue by giving them dedicated tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Initialize Subtabs
        self.sub_table = DataTable(self.notebook, self.controller)
        self.sub_variables = DataVariables(self.notebook, self.controller)
        self.sub_desc = DataDesc(self.notebook, self.controller)
        self.sub_model = DataModel(self.notebook, self.controller)

        # Add to Notebook
        self.notebook.add(self.sub_table, text="Tabela de Dados")
        self.notebook.add(self.sub_variables, text="Variáveis (Modelagem)")
        self.notebook.add(self.sub_desc, text="Estatística Descritiva")
        self.notebook.add(self.sub_model, text="Tratamento & Limpeza")

    def refresh_ui(self):
        """Called internally or externally to reload all views"""
        self.tools.update_status()
        self.sub_table.refresh_view()
        self.sub_variables.refresh_view()
        self.sub_desc.refresh_view()
        # self.sub_model.refresh_view() # If implemented

    # API for StatsController
    def get_selected_variables(self):
        return self.sub_variables.get_selection()