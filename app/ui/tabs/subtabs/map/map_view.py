import tkinter as tk
from tkinter import ttk, messagebox
try:
    from tkintermapview import TkinterMapView
except ImportError:
    TkinterMapView = None

class MapView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.markers = []
        self.poi_markers = []
        self.map_widget = None
        self.current_df = None 
        
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        if TkinterMapView is None:
            self.show_install_error()
            return

        map_container = ttk.Frame(self)
        map_container.grid(row=0, column=0, sticky="nsew")
        map_container.columnconfigure(0, weight=1)
        map_container.rowconfigure(0, weight=1)

        self.map_widget = TkinterMapView(map_container, corner_radius=0)
        self.map_widget.grid(row=0, column=0, sticky="nsew")
        
        self.map_widget.set_position(-3.7319, -38.5267) 
        self.map_widget.set_zoom(12)

    def show_install_error(self):
        msg = "Biblioteca 'tkintermapview' não encontrada.\nInstale: pip install tkintermapview"
        lbl = ttk.Label(self, text=msg, foreground="red", justify="center")
        lbl.grid(row=0, column=0)

    def get_color_gradient(self, value, min_v, max_v):
        """Returns a hex color from Blue (Low) to Red (High)"""
        if max_v == min_v: return "#0000FF"
        ratio = (value - min_v) / (max_v - min_v)
        # Clamp
        ratio = max(0, min(1, ratio))
        
        r = int(255 * ratio)
        b = int(255 * (1 - ratio))
        return f"#{r:02x}00{b:02x}"

    def sync_data_from_handler(self, status_label_widget, color_by_col=None):
        handler = None
        if hasattr(self.controller, 'data_handler'): handler = self.controller.data_handler
        elif hasattr(self.controller, 'main') and hasattr(self.controller.main, 'data_handler'):
            handler = self.controller.main.data_handler
        
        if not handler: return

        try:
            self.current_df = handler.get_data()
        except Exception: return

        if self.current_df is None or self.current_df.empty:
            if status_label_widget: status_label_widget.config(text="Tabela vazia", foreground="red")
            return

        # Identify Cols
        cols = [c.lower() for c in self.current_df.columns]
        lat_col = next((c for c in self.current_df.columns if c.lower() in ['lat', 'latitude']), None)
        lon_col = next((c for c in self.current_df.columns if c.lower() in ['lon', 'long', 'longitude']), None)
        
        if not lat_col or not lon_col:
            messagebox.showwarning("Aviso", "Colunas de coordenadas não encontradas.")
            return

        self.plot_markers(lat_col, lon_col, color_by_col)
        
        if status_label_widget: 
            status_label_widget.config(text=f"{len(self.markers)} pontos plotados", foreground="green")

    def plot_markers(self, lat_col, lon_col, color_by_col=None):
        if not self.map_widget: return
        self.map_widget.delete_all_marker()
        self.markers = []
        lats, lons = [], []

        # Determine Range for Color
        min_val, max_val = 0, 1
        if color_by_col and color_by_col in self.current_df.columns:
            try:
                vals = self.current_df[color_by_col].astype(float)
                min_val, max_val = vals.min(), vals.max()
            except: color_by_col = None # Fallback if non-numeric

        for _, row in self.current_df.iterrows():
            try:
                lat = float(row[lat_col])
                lon = float(row[lon_col])
                if lat == 0 and lon == 0: continue
                
                txt = f"ID: {row.get('id', '?')}"
                marker_color = None
                
                if color_by_col:
                    val = float(row[color_by_col])
                    txt += f"\n{color_by_col}: {val:.2f}"
                    marker_color = self.get_color_gradient(val, min_val, max_val)
                
                m = self.map_widget.set_marker(lat, lon, text=txt, marker_color_circle=marker_color, marker_color_outside=marker_color)
                self.markers.append(m)
                lats.append(lat); lons.append(lon)
            except: continue

        if lats and lons:
            top_left = (max(lats), min(lons))
            bottom_right = (min(lats), max(lons))
            try: self.map_widget.fit_bounding_box(top_left, bottom_right)
            except: pass

    def plot_pois(self, pois_list):
        """Plots Pole of Influence markers with distinct icon/color"""
        # Clear old POIs (we need to track them separately ideally, but for now clear all is risky if mixed)
        # TkinterMapView doesn't support deleting specific list easily without reference.
        # Simple approach: redraw all markers + POIs. For now, just add POIs on top.
        
        for p in pois_list:
            try:
                # Use a distinct color (e.g., Green or Yellow)
                m = self.map_widget.set_marker(
                    float(p['lat']), 
                    float(p['lon']), 
                    text=f"POI: {p['name']}",
                    marker_color_circle="#00FF00",
                    marker_color_outside="#00AA00"
                )
                self.poi_markers.append(m)
            except: pass