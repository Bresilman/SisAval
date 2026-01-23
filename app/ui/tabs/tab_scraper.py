import tkinter as tk
from tkinter import ttk
from app.ui.tabs.subtabs.scraper.scraper_run import ScraperRunSubTab
from app.ui.tabs.subtabs.scraper.scraper_calibrate import ScraperCalibrateSubTab
from app.ui.tabs.subtabs.scraper.scraper_config import ScraperConfigSubTab

class ScraperTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # 1. Run
        self.sub_run = ScraperRunSubTab(self.notebook, self.controller)
        self.notebook.add(self.sub_run, text="1. Importação em Massa")

        # 2. Calibrate
        self.sub_calib = ScraperCalibrateSubTab(self.notebook, self.controller)
        self.notebook.add(self.sub_calib, text="2. Calibrador (Treinar)")

        # 3. Config
        self.sub_conf = ScraperConfigSubTab(self.notebook, self.controller)
        self.notebook.add(self.sub_conf, text="3. Configurações")