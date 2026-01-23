import tkinter as tk
from tkinter import ttk, messagebox
from app.ui.tabs.subtabs.settings_ident import SettingsIdentSubTab
from app.ui.tabs.subtabs.settings_stats import SettingsStatsSubTab
from app.ui.tabs.subtabs.settings_eng import SettingsEngSubTab

class SettingsTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # 1. Identification
        self.sub_ident = SettingsIdentSubTab(self.notebook)
        self.notebook.add(self.sub_ident, text="🆔 Identificação")

        # 2. Statistics
        self.sub_stats = SettingsStatsSubTab(self.notebook)
        self.notebook.add(self.sub_stats, text="📊 Estatística")

        # 3. Engineering
        self.sub_eng = SettingsEngSubTab(self.notebook)
        self.notebook.add(self.sub_eng, text="🏗️ Engenharia")

        # Global Save Button
        fr_bot = ttk.Frame(self, padding=10)
        fr_bot.pack(fill='x')
        ttk.Button(fr_bot, text="💾 Salvar Configurações (Sessão)", command=self.salvar_configs).pack(side='right')

    def salvar_configs(self):
        # Gets data from all subtabs
        cfg = self.get_settings()
        # Here we could save to a JSON file on disk for persistence
        # For now, just a confirmation
        messagebox.showinfo("Configurações", "Configurações aplicadas para esta sessão!")

    def get_settings(self):
        # Merges all dicts
        s1 = self.sub_ident.get_data()
        s2 = self.sub_stats.get_data()
        s3 = self.sub_eng.get_data()
        
        # Merge all into one dict
        return {**s1, **s2, **s3}