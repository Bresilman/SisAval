import tkinter as tk
from tkinter import ttk, Menu, messagebox
from app.config import settings

# Import das Abas Modulares
from app.ui.tabs.tab_data import DataTab
from app.ui.tabs.tab_regression import RegressionTab
from app.ui.tabs.tab_validation import ValidationTab
from app.ui.tabs.tab_calculator import CalculatorTab
from app.ui.tabs.tab_optimizer import OptimizerTab
from app.ui.tabs.tab_evolutionary import EvolutionaryTab
from app.ui.tabs.tab_settings import SettingsTab
from app.ui.tabs.tab_plots import PlotsTab
from app.ui.tabs.tab_factors import FactorsTab
from app.ui.tabs.tab_map import MapTab
from app.ui.tabs.tab_databank import DatabankTab # NOVO
from app.ui.tabs.tab_report import ReportTab
from app.ui.tabs.tab_scraper import ScraperTab

class MainWindow(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title(settings.APP_TITLE)
        self.geometry(settings.APP_SIZE)
        self._setup_menu() # Menu Superior
        self._setup_ui()

    def _setup_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)

        # Menu Arquivo
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="📂 Abrir Projeto", command=self.controller.acao_abrir_projeto)
        file_menu.add_command(label="💾 Salvar Projeto", command=self.controller.acao_salvar_projeto)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        # Menu Ajuda
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre", command=lambda: messagebox.showinfo("Sobre", "SisAval - Avaliação de Imóveis\nVersão 1.0"))
        menubar.add_cascade(label="Ajuda", menu=help_menu)

    def _setup_ui(self):
        # Notebook Principal
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 1. Aba de Dados
        self.tab_data = DataTab(self.notebook, self.controller)
        self.notebook.add(self.tab_data, text="1. Dados")

        # 2. Aba de Regressão
        self.tab_regression = RegressionTab(self.notebook, self.controller)
        self.notebook.add(self.tab_regression, text="2. Estatística")

        # 3. Aba de Gráficos Detalhados
        self.tab_plots = PlotsTab(self.notebook, self.controller)
        self.notebook.add(self.tab_plots, text="3. Gráficos")

        # 4. Aba de Validação
        self.tab_validation = ValidationTab(self.notebook)
        self.notebook.add(self.tab_validation, text="4. Validação NBR")

        # 5. Aba Otimizador
        self.tab_optimizer = OptimizerTab(self.notebook, self.controller)
        self.notebook.add(self.tab_optimizer, text="5. Otimizador")

        # 6. Aba Calculadora
        self.tab_calculator = CalculatorTab(self.notebook, self.controller)
        self.notebook.add(self.tab_calculator, text="6. Calculadora")

        # 7. Aba Evolutiva
        self.tab_evolutionary = EvolutionaryTab(self.notebook, self.controller)
        self.notebook.add(self.tab_evolutionary, text="7. Evolutivo")
        
        # 8. Aba Fatores
        self.tab_factors = FactorsTab(self.notebook, self.controller)
        self.notebook.add(self.tab_factors, text="8. Fatores")

        # 9. Aba Mapa
        self.tab_map = MapTab(self.notebook, self.controller)
        self.notebook.add(self.tab_map, text="9. Mapa")
        
        # 10. Databank
        self.tab_databank = DatabankTab(self.notebook, self.controller)
        self.notebook.add(self.tab_databank, text="10. Banco de Dados")

        # 11. Scraper (NEW)
        self.tab_scraper = ScraperTab(self.notebook, self.controller)
        self.notebook.add(self.tab_scraper, text="11. Web Scraper")

        # 12. Aba Configurações
        self.tab_settings = SettingsTab(self.notebook, self.controller)
        self.notebook.add(self.tab_settings, text="⚙️ Configurações")

        self.tab_report = ReportTab(self.notebook, self.controller)
        self.notebook.add(self.tab_report, text="12. Relatório PDF")