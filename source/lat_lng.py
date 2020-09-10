from typing import List
from warnings import warn

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

    def distanceTo(self, other):
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

    @staticmethod
    def midpoint(positions:List['LatLng'])->'LatLng':
        if len(positions) < 1:
            raise Exception("Could not calculate midpoint of single coordinate")
        if len(positions) ==1:
            warn("Calculating midpoint of 1 element")
            return positions[0]

        x = 0
        y = 0
        z = 0
        w = 1.0 / float(len(positions))
        for platlng in positions:
            p = platlng.spherical_coordinate
            x += p[0] * w
            y += p[1] * w
            z += p[2] * w

        return LatLng.from_3d(x,y,z)



    @staticmethod
    def from_3d(x,y,z)->'LatLng':
        lng = math.atan2(y,x)
        hyp = math.sqrt(x*x+y*y)
        lat = math.atan2(z,hyp)
        return LatLng(math.degrees(lat),math.degrees(lng))

    @property
    def spherical_coordinate(self):
        lat = math.radians(self.lat)
        lng = math.radians(self.lng)
        x = math.cos(lat) * math.cos(lng)
        y = math.cos(lat) * math.sin(lng)
        z = math.sin(lat)
        return (x, y, z)

    def approxMidpoint(self, other):
        return LatLng((self.lat + other.lat) * .5, (self.lng + other.lng) * .5)
