import tkinter as tk
from tkinter import ttk, messagebox

try:
    import tkintermapview
    MAP_AVAILABLE = True
except ImportError:
    MAP_AVAILABLE = False

class MapViewSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.map_widget = None
        self._setup_ui()

    def _setup_ui(self):
        if not MAP_AVAILABLE:
            ttk.Label(self, text="Biblioteca 'tkintermapview' não instalada.\nExecute: pip install tkintermapview", foreground="red").pack(pady=20)
            return

        # Controls
        fr_top = ttk.Frame(self)
        fr_top.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(fr_top, text="📍 Plotar Pontos", command=self.plot_data).pack(side='left')
        ttk.Button(fr_top, text="🔥 Gerar Mapa de Calor (Heatmap)", command=self.plot_heatmap).pack(side='left', padx=10)
        
        # Tile Server Selection (Optional Polish)
        self.tile_server = tk.StringVar(value="OpenStreetMap")
        cb_tile = ttk.Combobox(fr_top, values=["OpenStreetMap", "Google Normal", "Google Satellite"], state="readonly", width=15)
        cb_tile.set("OpenStreetMap")
        cb_tile.pack(side='right')
        cb_tile.bind("<<ComboboxSelected>>", self._change_tile)

        # Map Widget
        self.fr_map = ttk.Frame(self)
        self.fr_map.pack(fill='both', expand=True)
        
        self.map_widget = tkintermapview.TkinterMapView(self.fr_map, width=800, height=600, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        
        # Set default position (Fortaleza/CE)
        self.map_widget.set_position(-3.7319, -38.5267) 
        self.map_widget.set_zoom(12)

    def _change_tile(self, event):
        selection = event.widget.get()
        if selection == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif selection == "Google Normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga")
        elif selection == "Google Satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga")

    def _get_data(self):
        df = self.controller.data_handler.get_data()
        if df is None: 
            messagebox.showwarning("Aviso", "Sem dados carregados.")
            return None
        
        # Check columns logic (Case insensitive check)
        cols_lower = {c.lower(): c for c in df.columns}
        
        lat_col = cols_lower.get('latitude') or cols_lower.get('lat')
        lon_col = cols_lower.get('longitude') or cols_lower.get('lon') or cols_lower.get('lng')
        
        if not lat_col or not lon_col:
            messagebox.showerror("Erro", "Sua planilha precisa ter colunas 'Latitude' e 'Longitude'.")
            return None
            
        return df, lat_col, lon_col

    def plot_data(self):
        res = self._get_data()
        if not res: return
        df, lat_c, lon_c = res

        self.map_widget.delete_all_marker()
        self.map_widget.delete_all_heatmap_elements() # Clear previous heatmaps
        
        markers = []
        for idx, row in df.iterrows():
            try:
                lat = float(row[lat_c])
                lon = float(row[lon_c])
                
                # Determine Value to show
                val = row.get('Valor_Unitario', row.get('Valor_Total', ''))
                if val: val = f"R$ {val:,.2f}"
                
                self.map_widget.set_marker(lat, lon, text=f"ID {idx}\n{val}")
                markers.append((lat, lon))
            except:
                pass
        
        if markers:
            self.map_widget.fit_bounding_box((max(x[0] for x in markers), min(x[1] for x in markers)),
                                             (min(x[0] for x in markers), max(x[1] for x in markers)))

    def plot_heatmap(self):
        """
        Uses the sample data itself to generate the heatmap.
        High values (expensive) = Red, Low values = Blue/Green.
        """
        res = self._get_data()
        if not res: return
        df, lat_c, lon_c = res
        
        # Ask which value to use for weight
        # Ideally we use 'Valor_Unitario' as it represents the 'heat' of the location better than total price
        val_col = 'Valor_Unitario'
        if val_col not in df.columns:
            # Fallback if specific column not found
            val_col = df.select_dtypes(include=['number']).columns[0]
            messagebox.showinfo("Heatmap", f"Usando coluna '{val_col}' para intensidade.")

        heatmap_data = []
        
        # Normalize values for heatmap intensity (0.0 to 1.0)
        # We need to handle outliers or the heatmap will be skewed
        try:
            vals = df[val_col].astype(float)
            min_v = vals.min()
            max_v = vals.max()
            
            for idx, row in df.iterrows():
                try:
                    lat = float(row[lat_c])
                    lon = float(row[lon_c])
                    raw_val = float(row[val_col])
                    
                    # Normalize: (val - min) / (max - min)
                    if max_v > min_v:
                        intensity = (raw_val - min_v) / (max_v - min_v)
                    else:
                        intensity = 0.5 # Default if all equal
                        
                    # Tuple: (lat, lon, intensity)
                    # Note: intensity determines color. 1.0 = Red, 0.0 = Blue/Transparent
                    heatmap_data.append((lat, lon, intensity))
                except: pass
                
            if heatmap_data:
                self.map_widget.delete_all_heatmap_elements() # Clear old
                # radius: controls how much the points blur together
                self.map_widget.set_heatmap(heatmap_data, radius=20, max_heat=1.0)
                messagebox.showinfo("Sucesso", "Mapa de Calor gerado com base nos valores da amostra!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar heatmap: {str(e)}")