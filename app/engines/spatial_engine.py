from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.distance import geodesic
import time
import pandas as pd

class SpatialEngine:
    def __init__(self):
        # User_agent is required by OpenStreetMap
        self.geolocator = Nominatim(user_agent="sisaval_app_tcc")

    def geocode_batch(self, df, address_col, city_col=None, progress_callback=None):
        """
        Converts addresses to Lat/Lon.
        Returns a list of dicts {index, lat, lon}.
        """
        results = []
        total = len(df)
        
        for i, (index, row) in enumerate(df.iterrows()):
            addr = str(row[address_col])
            if city_col and city_col in row:
                addr += f", {row[city_col]}"
            
            lat, lon = 0.0, 0.0
            status = "Erro"
            
            try:
                # Nominatim limits: 1 request per second
                time.sleep(1.1)
                location = self.geolocator.geocode(addr, timeout=10)
                if location:
                    lat, lon = location.latitude, location.longitude
                    status = "OK"
                else:
                    status = "Não encontrado"
            except:
                status = "Timeout"

            results.append({'index': index, 'lat': lat, 'lon': lon, 'status': status})
            
            if progress_callback:
                progress_callback(i + 1, total)

        return results

    def calculate_distances(self, df, lat_col, lon_col, target_lat, target_lon):
        """
        Calculates distance (in meters) from all points in DF to a Target Point.
        Returns a list of distances.
        """
        distances = []
        target = (target_lat, target_lon)
        
        for _, row in df.iterrows():
            try:
                origin = (row[lat_col], row[lon_col])
                # geodesic is more accurate than great_circle
                dist_meters = geodesic(origin, target).meters
                distances.append(dist_meters)
            except:
                distances.append(0.0)
                
        return distances