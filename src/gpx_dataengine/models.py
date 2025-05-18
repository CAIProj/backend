from dataclasses import dataclass
from typing import Optional, ClassVar
import math


@dataclass
class Point:
    """
    Represents a geographical point with coordinates in decimal degrees.

    Attributes:
        latitude (float):
            Latitude in decimal degrees (floating-point).
        longitude (float):
            Longitude in decimal degrees (floating-point).
        elevation (Optional[float]):
            Elevation in meters above sea level. Default is None.
    """
    latitude: float
    longitude: float
    elevation: Optional[float] = None

    # Class variable
    EARTH_RADIUS_KM: ClassVar[float] = 6371.0

    def to_dict(self) -> dict:
        """
        Convert the Point to a dictionary.

        Returns:
            dict: A mapping with keys'latitude' and 'longitude', and 'elevation' if available.
        """
        data = {'latitude': self.latitude, 'longitude': self.longitude}
        if self.elevation is not None:
            data['elevation'] = self.elevation
        return data
    
    @staticmethod
    def haversine_distance(p1: "Point", p2: "Point") -> float:
        """
        Calculates the Haversine distance between two points.

        Args:
            p1: The first point.
            p2: The second point.

        Returns:
            float: Distance between p1 and p2 in kilometers.
        """
        lat1, lon1 = math.radians(p1.latitude), math.radians(p1.longitude)
        lat2, lon2 = math.radians(p2.latitude), math.radians(p2.longitude)

        d_lat = lat2 - lat1
        d_lon = lon2 - lon1

        a = (math.sin(d_lat / 2) ** 2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return Point.EARTH_RADIUS_KM * c
    
    def distance_to(self, other: "Point") -> float:
        """
        Calculates the Haversine distance from this point to another.

        Args:
            other: The point to calculate distance to.

        Returns:
            float: Distance from this point to 'other' in kilometers.
        """
        return Point.haversine_distance(self, other)
    
    
class ElevationProfile:
    def __init__(self, points: list[Point]):
        """
        Initialize the ElevationProfile.

        Args:
            points (list[Point]): List of Point instances defining the route.
        """
        self.points = points
        self.distances = self._calculate_cumulative_distances()

    def _calculate_cumulative_distances(self) -> list[float]:
        """
        Compute the cumulative Haversine distances between consecutive points.

        Returns:
            list[float]: A list where each element is the total distance (in kilometers) from the start up to that point.
        """
        if len(self.points) < 2:
            return [0.0]

        distances = [0.0]
        for i in range(1, len(self.points)):
            distance = Point.haversine_distance(self.points[i - 1], self.points[i])
            distances.append(distances[-1] + distance)

        return distances

    def get_latitudes(self) -> list[float]:
        """
        Extract all latitudes from the profile points.

        Returns:
            list[float]: Latitudes of each Point in order.
        """
        return [p.latitude for p in self.points]

    def get_longitudes(self) -> list[float]:
        """
        Extract all longitudes from the profile points.

        Returns:
            list[float]: Longitudes of each Point in order.
        """
        return [p.longitude for p in self.points]

    def get_elevations(self) -> list[float]:
        """
        Extract all elevations from the profile points.

        Returns:
            list[float]: Elevations of each Point in order (may include None).
        """
        return [p.elevation for p in self.points]

    def get_distances(self) -> list[float]:
        """
        Retrieve the precomputed cumulative distances.

        Returns:
            list[float]: Cumulative distances (in kilometers) at each point.
        """
        return self.distances

    def set_elevations(self, elevations: list[float]) -> None:
        """
        Update the elevation values of all profile points.

        Args:
            elevations (list[float]): New elevation values in the same order and length as self.points.

        Raises:
            ValueError: If the length of elevations does not match the number of points in this profile.
        """
        if len(self.points) == len(elevations):
            for i, elevation in enumerate(elevations):
                self.points[i].elevation = elevation
        else:
            raise ValueError(
                'Length of the provided elevations should be same as number of points in the ElevationProfile')
