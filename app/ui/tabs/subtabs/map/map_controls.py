import tkinter as tk
from tkinter import ttk

class MapControls(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.map_view = None 
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        
        # --- Data Source ---
        lbl_data = ttk.LabelFrame(self, text="Fonte de Dados")
        lbl_data.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Button(lbl_data, text="🔄 Sincronizar Tudo", command=self.sync_data).pack(fill="x", padx=5, pady=5)
        self.lbl_status = ttk.Label(lbl_data, text="Aguardando...", foreground="gray")
        self.lbl_status.pack(pady=2)

        # --- Visualization Settings ---
        lbl_viz = ttk.LabelFrame(self, text="Visualização")
        lbl_viz.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Label(lbl_viz, text="Colorir por (Heatmap):").pack(anchor="w", padx=5)
        self.combo_heat = ttk.Combobox(lbl_viz, values=["(Padrão)", "preco", "area", "preco_m2"], state="readonly")
        self.combo_heat.current(0)
        self.combo_heat.pack(fill="x", padx=5, pady=5)
        self.combo_heat.bind("<<ComboboxSelected>>", self.sync_data)

        ttk.Label(lbl_viz, text="Estilo do Mapa:").pack(anchor="w", padx=5)
        self.combo_tile = ttk.Combobox(lbl_viz, values=["OpenStreetMap", "Google Normal", "Google Satellite"], state="readonly")
        self.combo_tile.current(0)
        self.combo_tile.pack(fill="x", padx=5, pady=5)
        self.combo_tile.bind("<<ComboboxSelected>>", self.change_tile_server)

    def set_map_view(self, map_view_instance):
        self.map_view = map_view_instance

    def sync_data(self, event=None):
        if not self.map_view: return
        
        # Determine Color Column
        col = self.combo_heat.get()
        if col == "(Padrão)": col = None
        
        self.map_view.sync_data_from_handler(self.lbl_status, color_by_col=col)

    def change_tile_server(self, event):
        if not self.map_view: return
        self.map_view.set_tile_server(self.combo_tile.get())