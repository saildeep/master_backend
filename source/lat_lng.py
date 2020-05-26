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
