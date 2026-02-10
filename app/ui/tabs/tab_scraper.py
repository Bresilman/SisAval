import tkinter as tk
from tkinter import ttk, messagebox

from app.controllers.scraper_controller import ScraperController
from app.ui.tabs.subtabs.scraper.scraper_run import ScraperRun
from app.ui.tabs.subtabs.scraper.scraper_config import ScraperConfig
from app.ui.tabs.subtabs.scraper.scraper_calibrate import ScraperCalibrate
# Import new subtab
from app.ui.tabs.subtabs.scraper.scraper_results import ScraperResults

class ScraperTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)
        self.parent = parent
        
        # Handle arguments
        self.main_app_controller = kwargs.get('controller')
        if not self.main_app_controller and args:
            self.main_app_controller = args[0]

        self.controller = ScraperController()
        self.setup_ui()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # 1. Run
        self.tab_run = ScraperRun(self.notebook, self.controller)
        self.notebook.add(self.tab_run, text="1. Coleta")

        # 2. Results (New Staging Area)
        # Pass main_app_controller so it can export data
        self.tab_results = ScraperResults(self.notebook, self.controller, self.main_app_controller)
        self.notebook.add(self.tab_results, text="2. Resultados (Staging)")

        # 3. Config
        self.tab_config = ScraperConfig(self.notebook, self.controller)
        self.notebook.add(self.tab_config, text="Configurações")

        # 4. Calibration
        self.tab_calibrate = ScraperCalibrate(self.notebook, self.controller)
        self.notebook.add(self.tab_calibrate, text="Calibração")