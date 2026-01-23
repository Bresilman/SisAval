from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

class GeocodingEngine:
    def __init__(self, user_agent="sisaval_app"):
        # Nominatim requires a unique user_agent
        self.geolocator = Nominatim(user_agent=user_agent)

    def geocode_address(self, address):
        """
        Converts 'Address, City' into (lat, lon).
        Returns None if not found.
        """
        try:
            # Add timeout to prevent hanging
            location = self.geolocator.geocode(address, timeout=10)
            if location:
                return location.latitude, location.longitude
            return None
        except (GeocoderTimedOut, GeocoderUnavailable):
            return None

    def batch_geocode(self, dataframe, address_col, city_col=None):
        """
        Geocodes an entire DataFrame column.
        """
        results = []
        for index, row in dataframe.iterrows():
            addr = str(row[address_col])
            
            # Append city if provided for better accuracy
            if city_col and city_col in row:
                city = str(row[city_col])
                full_address = f"{addr}, {city}"
            else:
                full_address = addr

            # Nominatim Policy: Max 1 request per second
            time.sleep(1.1) 
            
            coords = self.geocode_address(full_address)
            
            if coords:
                results.append({'index': index, 'lat': coords[0], 'lon': coords[1], 'status': 'OK'})
            else:
                results.append({'index': index, 'lat': 0, 'lon': 0, 'status': 'Not Found'})
                
        return results