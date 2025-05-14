from gpxdata import Point
from math import radians, sin, cos, atan2, sqrt


class GeoCalculator:
    EARTH_RADIUS_KM = 6371.0

    @staticmethod
    def haversine_distance(point1: Point, point2: Point) -> float:
        lat1, lon1 = radians(point1.latitude), radians(point1.longitude)
        lat2, lon2 = radians(point2.latitude), radians(point2.longitude)

        d_lat = lat2 - lat1
        d_lon = lon2 - lon1

        a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return GeoCalculator.EARTH_RADIUS_KM * c


class ElevationProfile:
    def __init__(self, points: list[Point]):
        self.points = points
        self.distances = self._calculate_cumulative_distances()

    def _calculate_cumulative_distances(self) -> list[float]:
        if len(self.points) < 2:
            return [0.0]

        distances = [0.0]
        for i in range(1, len(self.points)):
            distance = GeoCalculator.haversine_distance(self.points[i - 1], self.points[i])
            distances.append(distances[-1] + distance)

        return distances

    def get_latitudes(self) -> list[float]:
        return [p.latitude for p in self.points]

    def get_longitudes(self) -> list[float]:
        return [p.longitude for p in self.points]

    def get_elevations(self) -> list[float]:
        return [p.elevation for p in self.points]

    def get_distances(self) -> list[float]:
        return self.distances

    def set_elevations(self, elevations: list[float]) -> None:
        if len(self.points) == len(elevations):
            for i, elevation in enumerate(elevations):
                self.points[i].elevation = elevation
        else:
            raise ValueError(
                'Length of the provided elevations should be same as number of points in the ElevationProfile')

