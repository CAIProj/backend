from pygeodesy import GeoidKarney
from pygeodesy.ellipsoidalKarney import LatLon
import gpxpy
from dataclasses import dataclass
import math
from typing import Optional, ClassVar
import os
import numpy as np
from scipy.interpolate import interp1d
# BaseEelevationAPI is used as string annotation when needed not imported - to avoid circular import issues. 

script_dir = os.path.dirname(os.path.abspath(__file__))
geoid_file = 'egm2008-5.pgm'

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
            dict: A mapping with keys 'latitude', 'longitude', and 'elevation' if available.
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

    def copy(self) -> "Point":
        """
        Create a copy of this Point.

        Returns:
            Point: A new Point instance with the same latitude, longitude, and elevation.
        """
        return Point(self.latitude, self.longitude, self.elevation)

    
    
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
        
    def get_elevation_stats(self) -> tuple[float, float, float, float]:
        """
        Returns elevation metrics for the profile.

        Returns:
            tuple: (ascend, descend, greatest_ascend, greatest_descend)
        """
        ascend = 0
        descend = 0
        greatest_ascend = 0
        greatest_descend = 0
        elevations = self.get_elevations()

        for i in range(len(elevations) - 1):
            delta = elevations[i + 1] - elevations[i]
            if delta > 0:
                ascend += delta
                greatest_ascend = max(greatest_ascend, delta)
            else:
                descend += abs(delta)
                greatest_descend = max(greatest_descend, abs(delta))

        return ascend, descend, greatest_ascend, greatest_descend
    
    def copy(self) -> "ElevationProfile":
        """
        Create a deep copy of this ElevationProfile.

        Returns:
            ElevationProfile: A new instance with duplicated Points and distances.
        """
        new_points = [p.copy() for p in self.points]
        return ElevationProfile(new_points)
    
    def set_distances(self, distances: list[float]) -> None:
        """
        Update the cumulative distances of the profile.

        This method allows overriding the automatically calculated distances,
        which can be useful for customized visualizations or comparisons.

        Args:
            distances (list[float]): New cumulative distances (in kilometers) corresponding to each point.

        Raises:
            ValueError: If the length of distances does not match the number of points in this profile.
        """
        if len(self.distances) == len(distances):
            for i, distance in enumerate(distances):
                self.distances[i] = distance
        else:
            raise ValueError('Length of the provided distances should be the same as the number of points in the Elevation Profile')
    
    def with_api_elevations(self, api_cls: type["BaseElevationAPI"]) -> "ElevationProfile":
        """
        Return a new ElevationProfile with elevations fetched from the specified API.

        Args:
            api_cls (type[BaseElevationAPI]): Elevation API class to fetch elevation data.

        Returns:
            ElevationProfile: A new profile with updated elevation values.

        Raises:
            ValueError: If the number of elevations returned by the API does not match the number of points.
        """
        elevations = api_cls.get_elevations(self.points)
        
        if len(elevations) != len(self.points):
            raise ValueError("Elevation API returned a mismatched number of elevations.")

        new_profile = self.copy()
        new_profile.set_elevations(elevations)
        return new_profile


class Track:
    def __init__(self, points: list[Point]):
        """
        Initialize a Track with a list of Points.

        Args:
            points (list[Point]): Ordered list of geographical Points.
        """
        self._points = list(points)
        self._elevation_profile: Optional[ElevationProfile] = None
        self._total_distance: Optional[float] = None

    @property
    def points(self) -> list[Point]:
        """
        Gets the list of Points in the track.

        Returns:
            list[Point]: Ordered list of geographical Points.
        """
        return self._points
    
    @points.setter
    def points(self, new_points: list[Point]) -> None:
        """
        Sets the list of Points in the track and resets the elevation profile.

        Args:
            new_points (list[Point]): New list of Points to replace the current one.

        Raises:
            ValueError: If the input is not a list of Points.
        """
        if not isinstance(new_points, list) or not all(isinstance(p, Point) for p in new_points):
            raise ValueError("points must be a list of Point instances.")
        self._points = new_points
        self._elevation_profile = None
        self._total_distance = None

    @property
    def elevation_profile(self) -> ElevationProfile:
        """
        Provides the ElevationProfile for this Track based on the current points.

        Returns:
            ElevationProfile: Elevation profile created from the track's points.
        """
        if self._elevation_profile is None:
            self._elevation_profile = ElevationProfile(self.points)
        return self._elevation_profile
    
    @property
    def total_distance(self) -> float:
        """
        Compute the total Haversine distance of the track in kilometers.

        Returns:
            float: Total distance (in kilometers) from the start up to that point.
        """
        if self._total_distance is None:
            if len(self._points) < 2:
                self._total_distance = 0.0
            else:
                distance = 0.0
                for i in range(len(self._points) - 1):
                    distance += self._points[i].distance_to(self._points[i + 1])
                self._total_distance = distance

        return self._total_distance

    @classmethod
    def from_gpx_file(cls, gpx_file_path: str) -> 'Track':
        """
        Factory method to load a Track from a GPX file.

        Args:
            gpx_file_path (str): Path to a GPX file containing track data.

        Returns:
            Track: Instance with Points extracted from the GPX.

        Raises:
            FileNotFoundError: If the GPX file is not found.
            IOError: If there is an error reading the file.
            ValueError: If the GPX content cannot be parsed.
        """
        # Read the gpx file
        try:
            with open(gpx_file_path, 'r', encoding='utf-8') as f:
                gpx_text = f.read()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"GPX file not found: {gpx_file_path}") from e
        except Exception as e:
            raise IOError(f"Error reading GPX file: {gpx_file_path}") from e

        # Parse the file content
        try:
            gpx = gpxpy.parse(gpx_text)
        except Exception as e:
            raise ValueError(f"Failed to parse GPX content from: {gpx_file_path}") from e

        points: list[Point] = []
        geoid = GeoidKarney(os.path.join(script_dir, geoid_file))
        for tr in gpx.tracks:
            for seg in tr.segments:
                for pt in seg.points:
                    location = LatLon(pt.latitude, pt.longitude)
                    height = geoid(location)
                    points.append(Point(latitude=pt.latitude, longitude=pt.longitude,
                                        elevation=pt.elevation - height))
        return cls(points)

    def get_latitudes(self) -> list[float]:
        """
        Returns the list of latitudes for all Points in the track.

        Returns:
            list[float]: Latitudes of the points in the track.
        """
        return [p.latitude for p in self.points]

    def get_longitudes(self) -> list[float]:
        """
        Returns the list of longitudes for all Points in the track.

        Returns:
            list[float]: Longitudes of the points in the track.
        """
        return [p.longitude for p in self.points]

    def get_elevations(self) -> list[Optional[float]]:
        """
        Returns the list of elevations for all Points in the track.

        Returns:
            list[Optional[float]]: Elevations of the points in the track.
        """
        return [p.elevation for p in self.points]
    
    def set_elevations(self, elevations: list[float]) -> None:
        """
        Update the elevation values of all track points.

        Args:
            elevations (list[float]): New elevation values in the same order and length as the track points.

        Raises:
            ValueError: If the length of elevations does not match the number of points in the track.
        """
        if len(self.points) != len(elevations):
            raise ValueError("Length of the provided elevations must match the number of points in the Track")

        for i, elevation in enumerate(elevations):
            self._points[i].elevation = elevation

        if self._elevation_profile is not None:
            self._elevation_profile.set_elevations(elevations)
    
    def copy(self) -> "Track":
        """
        Create a deep copy of this Track, including all Points.

        Returns:
            Track: A new Track instance with duplicated Points.
        """
        copied_points = [p.copy() for p in self.points]
        return Track(copied_points)
    
    def with_api_elevations(self, api_cls: type["BaseElevationAPI"]) -> "Track":
        """
        Return a new Track instance with elevations fetched from the given API class.

        Args:
            api_cls (type[BaseElevationAPI]): The elevation API class to use.

        Returns:
            Track: A new Track with updated elevation data.

        Raises:
            ValueError: If the number of elevations returned does not match the number of points.
        """
        elevations = api_cls.get_elevations(self.points)
        
        if len(elevations) != len(self.points):
            raise ValueError("Elevation API returned a mismatched number of elevations.")

        new_track = self.copy()
        new_track.set_elevations(elevations)
        return new_track

    @staticmethod
    def interpolate_to_match_points(full_route: 'Track', subset_route: 'Track') -> 'Track':
        """
        Interpolates the first recording (full route) to match the number of points in the second recording (subset).
        
        This function is useful when comparing two GPX recordings where the second recording is a subset 
        of the first recording. It interpolates the latitude, longitude, and elevation of the full route
        to create a new track with the same number of points as the subset, enabling direct comparison.
        
        Args:
            full_route (Track): The complete route recording to be interpolated
            subset_route (Track): The subset recording that determines the target number of points
            
        Returns:
            Track: A new Track instance with the full route interpolated to match the subset's point count
            
        Raises:
            ValueError: If either track has fewer than 2 points or if interpolation fails
        """
        if len(full_route.points) < 2:
            raise ValueError("Full route must have at least 2 points for interpolation")
        if len(subset_route.points) < 2:
            raise ValueError("Subset route must have at least 2 points")
            
        # Calculate cumulative distances for the full route
        full_distances = full_route.elevation_profile.get_distances()
        full_lats = full_route.get_latitudes()
        full_lons = full_route.get_longitudes()
        full_elevations = full_route.get_elevations()
        
        # Handle None elevations by replacing with 0 for interpolation
        full_elevations_clean = [elev if elev is not None else 0.0 for elev in full_elevations]
        
        # Calculate target distances based on the subset track length
        target_count = len(subset_route.points)
        total_distance = full_distances[-1]
        
        # Create evenly spaced distance values for interpolation
        target_distances = np.linspace(0, total_distance, target_count)
        
        try:
            # Create interpolation functions for each coordinate
            lat_interp = interp1d(full_distances, full_lats, kind='linear', bounds_error=False, fill_value='extrapolate')
            lon_interp = interp1d(full_distances, full_lons, kind='linear', bounds_error=False, fill_value='extrapolate')
            elev_interp = interp1d(full_distances, full_elevations_clean, kind='linear', bounds_error=False, fill_value='extrapolate')
            
            # Interpolate coordinates at target distances
            interpolated_lats = lat_interp(target_distances)
            interpolated_lons = lon_interp(target_distances)
            interpolated_elevs = elev_interp(target_distances)
            
            # Create interpolated points
            interpolated_points = []
            for i in range(target_count):
                # Restore None elevations if original full route had None values
                elevation = float(interpolated_elevs[i]) if any(e is not None for e in full_elevations) else None
                point = Point(
                    latitude=float(interpolated_lats[i]),
                    longitude=float(interpolated_lons[i]),
                    elevation=elevation
                )
                interpolated_points.append(point)
                
            return Track(interpolated_points)
            
        except Exception as e:
            raise ValueError(f"Failed to interpolate track: {str(e)}") from e

    @staticmethod
    def align_track_endpoints(track1: 'Track', track2: 'Track', tolerance_km: float = 0.1) -> tuple['Track', 'Track']:
        """
        Aligns two GPX tracks by truncating them so they start and end at approximately the same positions.
        
        This function is useful when comparing two recordings of the same route that may have been started
        or stopped at slightly different points. It finds the best matching start and end points within
        the specified tolerance and returns truncated versions of both tracks.
        
        Args:
            track1 (Track): First GPX track to align
            track2 (Track): Second GPX track to align  
            tolerance_km (float): Maximum distance in kilometers to consider points as matching (default: 0.1km = 100m)
            
        Returns:
            tuple[Track, Track]: Aligned versions of track1 and track2 with matching start/end positions
            
        Raises:
            ValueError: If tracks have insufficient points or no suitable alignment can be found
        """
        if len(track1.points) < 2 or len(track2.points) < 2:
            raise ValueError("Both tracks must have at least 2 points for alignment")
            
        # Find best start alignment
        start1_idx, start2_idx = Track._find_best_start_alignment(track1, track2, tolerance_km)
        if start1_idx is None or start2_idx is None:
            raise ValueError(f"Cannot find matching start points within {tolerance_km}km tolerance")
            
        # Find best end alignment (working backwards from the end)
        end1_idx, end2_idx = Track._find_best_end_alignment(track1, track2, tolerance_km)
        if end1_idx is None or end2_idx is None:
            raise ValueError(f"Cannot find matching end points within {tolerance_km}km tolerance")
            
        # Ensure we have valid ranges after alignment
        if start1_idx >= end1_idx or start2_idx >= end2_idx:
            raise ValueError("Alignment would result in empty or invalid track segments")
            
        # Create aligned tracks by slicing the point arrays
        aligned_points1 = track1.points[start1_idx:end1_idx + 1]
        aligned_points2 = track2.points[start2_idx:end2_idx + 1]
        
        return Track(aligned_points1), Track(aligned_points2)
    
    @staticmethod
    def _find_best_start_alignment(track1: 'Track', track2: 'Track', tolerance_km: float) -> tuple[Optional[int], Optional[int]]:
        """
        Finds the best starting point alignment between two tracks.
        
        Returns:
            tuple[Optional[int], Optional[int]]: Indices of best matching start points, or (None, None) if no match found
        """
        best_distance = float('inf')
        best_indices = (None, None)
        
        # Search within first 20% of each track for start alignment
        search_limit1 = max(1, len(track1.points) // 5)
        search_limit2 = max(1, len(track2.points) // 5)
        
        for i in range(search_limit1):
            for j in range(search_limit2):
                distance = track1.points[i].distance_to(track2.points[j])
                if distance <= tolerance_km and distance < best_distance:
                    best_distance = distance
                    best_indices = (i, j)
                    
        return best_indices
    
    @staticmethod
    def _find_best_end_alignment(track1: 'Track', track2: 'Track', tolerance_km: float) -> tuple[Optional[int], Optional[int]]:
        """
        Finds the best ending point alignment between two tracks.
        
        Returns:
            tuple[Optional[int], Optional[int]]: Indices of best matching end points, or (None, None) if no match found
        """
        best_distance = float('inf')
        best_indices = (None, None)
        
        # Search within last 20% of each track for end alignment
        search_start1 = len(track1.points) - max(1, len(track1.points) // 5)
        search_start2 = len(track2.points) - max(1, len(track2.points) // 5)
        
        for i in range(search_start1, len(track1.points)):
            for j in range(search_start2, len(track2.points)):
                distance = track1.points[i].distance_to(track2.points[j])
                if distance <= tolerance_km and distance < best_distance:
                    best_distance = distance
                    best_indices = (i, j)
                    
        return best_indices