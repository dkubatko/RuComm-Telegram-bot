import googlemaps

class GoogleMapsAPI:
    def __init__(self, key):
        self.client = googlemaps.Client(key=key)

    def find_place_nearby(self, location, query):
        result = self.client.places_nearby(location=location, 
            keyword=query, 
            rank_by="distance")
        
        if (not (result.get('status', 'ZERO_RESULTS') in ['ZERO_RESULTS', 'INVALID_REQUEST'])):
            return result['results'][0]['geometry']['location']
        else:
            return None