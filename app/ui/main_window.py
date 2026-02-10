import tkinter as tk
from tkinter import ttk
import sys
import os

# Adiciona o diretório raiz ao path para garantir que as importações funcionem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Importação das Abas (Views)
# FIX: Corrected import from DataTab to TabData
from app.ui.tabs.tab_data import TabData
from app.ui.tabs.tab_map import MapTab
from app.ui.tabs.tab_factors import FactorsTab
from app.ui.tabs.tab_regression import RegressionTab
from app.ui.tabs.tab_plots import PlotsTab
from app.ui.tabs.tab_validation import ValidationTab
from app.ui.tabs.tab_calculator import CalculatorTab
from app.ui.tabs.tab_report import ReportTab
from app.ui.tabs.tab_settings import SettingsTab
from app.ui.tabs.tab_scraper import ScraperTab
from app.ui.tabs.tab_databank import DatabankTab
from app.ui.tabs.tab_evolutionary import EvolutionaryTab
from app.ui.tabs.tab_optimizer import OptimizerTab
from app.ui.tabs.tab_urban import UrbanTab
from app.ui.tabs.tab_google import GoogleTab

class MainWindow(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("SisAval - Sistema de Avaliação de Imóveis (Alpha)")
        self.geometry("1400x900")
        
        # Configuração de Estilo (Tema)
        style = ttk.Style(self)
        style.theme_use('clam') 
        
        self.setup_ui()

    def setup_ui(self):
        # Container Principal
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Notebook (Abas)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)

        # --- Inicialização das Abas ---
        
        # 1. Dados (Data Tab)
        # FIX: Instantiating TabData instead of DataTab
        self.tab_data = TabData(self.notebook, self.controller)
        self.notebook.add(self.tab_data, text="1. Dados")

        # 2. Mapa (Map Tab)
        self.tab_map = MapTab(self.notebook, self.controller)
        self.notebook.add(self.tab_map, text="2. Mapa")

        # 3. Fatores (Factors Tab)
        self.tab_factors = FactorsTab(self.notebook, self.controller)
        self.notebook.add(self.tab_factors, text="3. Fatores")

        # 4. Regressão (Regression Tab)
        self.tab_regression = RegressionTab(self.notebook, self.controller)
        self.notebook.add(self.tab_regression, text="4. Regressão")

        # 5. Gráficos (Plots Tab)
        self.tab_plots = PlotsTab(self.notebook, self.controller)
        self.notebook.add(self.tab_plots, text="5. Gráficos")

        # 6. Validação (Validation Tab)
        self.tab_validation = ValidationTab(self.notebook, self.controller)
        self.notebook.add(self.tab_validation, text="6. Validação")

        # 7. Calculadora (Calculator Tab)
        self.tab_calculator = CalculatorTab(self.notebook, self.controller)
        self.notebook.add(self.tab_calculator, text="7. Calculadora")

        # 8. Relatório (Report Tab)
        self.tab_report = ReportTab(self.notebook, self.controller)
        self.notebook.add(self.tab_report, text="8. Relatório")

        # --- Abas Extras/Ferramentas ---
        
        self.tab_scraper = ScraperTab(self.notebook, controller=self.controller)
        self.notebook.add(self.tab_scraper, text="Scraper")

        self.tab_databank = DatabankTab(self.notebook, self.controller)
        self.notebook.add(self.tab_databank, text="Banco de Dados")

        self.tab_evolutionary = EvolutionaryTab(self.notebook, self.controller)
        self.notebook.add(self.tab_evolutionary, text="Algoritmo Genético")

        self.tab_optimizer = OptimizerTab(self.notebook, self.controller)
        self.notebook.add(self.tab_optimizer, text="Otimizador")
        
        self.tab_urban = UrbanTab(self.notebook, self.controller)
        self.notebook.add(self.tab_urban, text="Variáveis Urbanas")
        
        self.tab_google = GoogleTab(self.notebook, self.controller)
        self.notebook.add(self.tab_google, text="Google API")

        self.tab_settings = SettingsTab(self.notebook, self.controller)
        self.notebook.add(self.tab_settings, text="Configurações")

    def show_error(self, message):
        from tkinter import messagebox
        messagebox.showerror("Erro", message)

    def show_info(self, message):
        from tkinter import messagebox
        messagebox.showinfo("Informação", message)