import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import numpy as np
import math

class MapVars(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Points of Interest (POIs) Storage
        self.pois = [
            {"name": "Centro da Cidade", "lat": -3.717, "lon": -38.543, "type": "Reference"},
            {"name": "Praia / Orla", "lat": -3.719, "lon": -38.510, "type": "Valorizante"}
        ]
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- 1. POI Management ---
        poi_frame = ttk.LabelFrame(self, text="Polos de Influência (POIs)")
        poi_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Toolbar
        btn_frame = ttk.Frame(poi_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(btn_frame, text="+ Adicionar Polo", command=self.add_poi).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="- Remover Selecionado", command=self.remove_poi).pack(side="left", padx=2)
        
        # POI List
        cols = ("name", "lat", "lon", "type")
        self.tree_pois = ttk.Treeview(poi_frame, columns=cols, show="headings", height=5)
        self.tree_pois.heading("name", text="Nome")
        self.tree_pois.heading("lat", text="Latitude")
        self.tree_pois.heading("lon", text="Longitude")
        self.tree_pois.heading("type", text="Tipo")
        
        self.tree_pois.column("name", width=150)
        self.tree_pois.column("lat", width=80)
        self.tree_pois.column("lon", width=80)
        self.tree_pois.column("type", width=100)
        
        self.tree_pois.pack(fill="x", padx=5, pady=5)
        self.refresh_poi_list()

        # --- 2. Calculation Actions ---
        calc_frame = ttk.LabelFrame(self, text="Cálculo de Distâncias")
        calc_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        ttk.Label(calc_frame, text="Selecione um Polo acima e clique para calcular a distância de todos os imóveis até ele.").pack(pady=10)
        
        ttk.Button(calc_frame, text="Calcular Distância e Adicionar à Tabela", command=self.calculate_distance).pack(fill="x", padx=20, pady=5)
        
        # Log
        self.lbl_result = ttk.Label(calc_frame, text="Aguardando ação...", foreground="gray")
        self.lbl_result.pack(pady=5)

    def refresh_poi_list(self):
        for item in self.tree_pois.get_children():
            self.tree_pois.delete(item)
        for p in self.pois:
            self.tree_pois.insert("", "end", values=(p['name'], p['lat'], p['lon'], p['type']))

    def add_poi(self):
        # Simple dialogs for prototype (In prod, use a proper form)
        name = simpledialog.askstring("Novo Polo", "Nome do Polo (ex: Shopping):")
        if not name: return
        lat = simpledialog.askfloat("Coordenada", "Latitude (ex: -3.71):")
        if lat is None: return
        lon = simpledialog.askfloat("Coordenada", "Longitude (ex: -38.54):")
        if lon is None: return
        
        self.pois.append({"name": name, "lat": lat, "lon": lon, "type": "User"})
        self.refresh_poi_list()
        
        # Update Map View if possible
        self._update_map_pois()

    def remove_poi(self):
        sel = self.tree_pois.selection()
        if not sel: return
        for item in sel:
            val = self.tree_pois.item(item)['values']
            self.pois = [p for p in self.pois if p['name'] != val[0]]
        self.refresh_poi_list()
        self._update_map_pois()

    def _update_map_pois(self):
        """Notifies the map view to show these POIs"""
        # Access MapView via Controller -> Main -> MapTab -> ViewPanel
        # Assuming controller structure: self.controller.main.view.tab_map.view_panel
        try:
            view_panel = self.controller.main.view.tab_map.view_panel
            view_panel.plot_pois(self.pois)
        except AttributeError:
            pass

    def calculate_distance(self):
        sel = self.tree_pois.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um Polo na lista acima.")
            return
            
        poi_data = self.tree_pois.item(sel[0])['values']
        poi_name, poi_lat, poi_lon = poi_data[0], float(poi_data[1]), float(poi_data[2])
        
        # Get Data
        handler = getattr(self.controller, 'data_handler', None) or getattr(self.controller.main, 'data_handler', None)
        if not handler: return
        
        df = handler.get_data()
        if df is None or df.empty: return

        # Haversine Vectorized
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371000 # meters
            phi1, phi2 = np.radians(lat1), np.radians(lat2)
            dphi = np.radians(lat2 - lat1)
            dlambda = np.radians(lon2 - lon1)
            a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2) * np.sin(dlambda/2)**2
            return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        # Check cols
        lat_col = next((c for c in df.columns if c.lower() in ['lat', 'latitude']), None)
        lon_col = next((c for c in df.columns if c.lower() in ['lon', 'long', 'longitude']), None)
        
        if not lat_col: 
            messagebox.showerror("Erro", "Colunas de coordenadas não encontradas nos dados.")
            return

        # Calculate
        col_name = f"dist_{poi_name.lower().replace(' ', '_')}"
        
        try:
            dists = haversine(df[lat_col].astype(float), df[lon_col].astype(float), poi_lat, poi_lon)
            
            # Save back to DataHandler
            # We need a method in data_handler to add a column. 
            # If pandas reference is shared, modifying 'df' might work if it's not a copy.
            df[col_name] = dists.round(2)
            
            # Notify User
            self.lbl_result.config(text=f"Coluna '{col_name}' criada com sucesso!", foreground="green")
            messagebox.showinfo("Sucesso", f"Distâncias calculadas! Nova variável criada: {col_name}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no cálculo: {e}")