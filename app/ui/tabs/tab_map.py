import tkinter as tk
from tkinter import ttk
from app.ui.tabs.subtabs.map.map_view import MapViewSubTab
from app.ui.tabs.subtabs.map.map_geocoding import MapGeocodingSubTab
from app.ui.tabs.subtabs.map.map_vars import MapVarsSubTab

class MapTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=5, pady=5)

        self.sub_view = MapViewSubTab(nb, self.controller)
        nb.add(self.sub_view, text="1. Visualização")

        self.sub_geo = MapGeocodingSubTab(nb, self.controller)
        nb.add(self.sub_geo, text="2. Geocodificação")

        self.sub_vars = MapVarsSubTab(nb, self.controller)
        nb.add(self.sub_vars, text="3. Variáveis Espaciais")