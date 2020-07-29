import math

class LatLng():
    def __init__(self, lat: float, lng: float):
        self.lat = lat
        self.lng = lng

    def assign(self, lat: float, lng: float):
        self.lat = lat
        self.lng = lng
        return self

    def __str__(self):
        return "LatLng:(" + str(self.lat) + "," + str(self.lng) + ")"

    def distanceTo(self,other):
        lat1 = self.lat
        lon1 = self.lng
        lat2 = other.lat
        lon2 = other.lng
        radius = 6371  # km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c

        return d

