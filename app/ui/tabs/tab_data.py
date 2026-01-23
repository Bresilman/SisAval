import tkinter as tk
from tkinter import ttk

# Import Subtabs
from app.ui.tabs.subtabs.data_table import DataTableSubTab
from app.ui.tabs.subtabs.data_model import DataModelSubTab
from app.ui.tabs.subtabs.data_tools import DataToolsSubTab  # New Import
from app.ui.tabs.subtabs.data_desc import DataDescSubTab

class DataTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # --- TOP PANEL (Global Actions) ---
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill='x')

        # File Buttons
        fr_file = ttk.Frame(top_frame)
        fr_file.pack(side='left')
        ttk.Button(fr_file, text="📂 Carregar Arquivo", command=self.controller.acao_carregar).pack(side='left', padx=2)
        ttk.Button(fr_file, text="🎲 Dados Exemplo", command=self.controller.acao_exemplo).pack(side='left', padx=2)
        
        # Calculate Button
        ttk.Button(top_frame, text="▶ CALCULAR REGRESSÃO", command=self.controller.acao_calcular).pack(side='right', padx=10)

        # --- MAIN NOTEBOOK ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # 1. Table Subtab
        self.subtab_table = DataTableSubTab(self.notebook, self.controller)
        self.notebook.add(self.subtab_table, text="📋 Tabela de Dados")

        # 2. Variable Definition Subtab
        self.subtab_model = DataModelSubTab(self.notebook, self.controller)
        self.notebook.add(self.subtab_model, text="⚙️ Definição de Variáveis")

        # 3. Engineering Tools Subtab (NEW)
        self.subtab_tools = DataToolsSubTab(self.notebook, self.controller)
        self.notebook.add(self.subtab_tools, text="🛠️ Ferramentas & Engenharia")

        # 4. Descriptive Statistics Subtab
        self.subtab_desc = DataDescSubTab(self.notebook)
        self.notebook.add(self.subtab_desc, text="📊 Estatística Descritiva")

    def update_table(self, df, numeric_cols):
        # Distribute updates to subtabs
        self.subtab_table.update_data(df)
        self.subtab_model.update_selectors(numeric_cols)
        self.subtab_desc.calculate_desc(df, numeric_cols)

    # --- PROXY PROPERTIES (Compatible with Controller) ---
    @property
    def combo_y(self):
        return self.subtab_model.combo_y
    
    @property
    def listbox_x(self):
        return self.subtab_model.listbox_x
    
    @property
    def var_log_global(self):
        # Now pointing to the tools subtab
        return self.subtab_tools.var_log_global
    
    @property
    def tree(self):
        return self.subtab_table.tree