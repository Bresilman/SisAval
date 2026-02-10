import tkinter as tk
from tkinter import ttk

# Import Subtabs
from app.ui.tabs.subtabs.map.map_controls import MapControls
from app.ui.tabs.subtabs.map.map_view import MapView
from app.ui.tabs.subtabs.map.map_geocoding import MapGeocoding
from app.ui.tabs.subtabs.map.map_vars import MapVars

class MapTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        # Create Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # --- TAB 1: Visualização ---
        # Container frame for the Split View (Map + Controls)
        tab_viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_viz_frame, text="Visualização do Mapa")
        
        # Grid Layout for Tab 1
        tab_viz_frame.columnconfigure(1, weight=1)
        tab_viz_frame.rowconfigure(0, weight=1)

        self.view_panel = MapView(tab_viz_frame, self.controller)
        self.controls_panel = MapControls(tab_viz_frame, self.controller)

        # Connect Logic
        self.controls_panel.set_map_view(self.view_panel)

        # Place Widgets
        self.controls_panel.grid(row=0, column=0, sticky="nsew")
        self.view_panel.grid(row=0, column=1, sticky="nsew")

        # --- TAB 2: Geocodificação ---
        self.tab_geo = MapGeocoding(self.notebook, self.controller)
        self.notebook.add(self.tab_geo, text="Geocodificação")

        # --- TAB 3: Variáveis Urbanas ---
        self.tab_vars = MapVars(self.notebook, self.controller)
        self.notebook.add(self.tab_vars, text="Variáveis Urbanas")