import time

import requests

# from lookup import *
import gpxpy
import gpxpy.gpx
from matplotlib import pyplot as plt
from dataclasses import dataclass
from typing import Optional
from math import radians, sin, cos, sqrt, atan2
from pygeodesy import GeoidKarney
from pygeodesy.ellipsoidalKarney import LatLon
import srtm
import json

OPEN_TOPOGRAPHY_API_KEY = "826940615389eccaac7f39dbee1218ca" #DO NOT PUBLISH

@dataclass
class Point:
    "Represents a geographical point (log, lat, elevation)"
    latitude: float
    longitude: float
    elevation: Optional[float] = None

    def to_dict(self):
        return {'latitude': self.latitude, 'longitude': self.longitude}
    
class GPXParser:
    "Extracts point from GPX files"

    @staticmethod
    def parse_gpx_file(file_path: str) -> list[Point]:
        try:
            with open(file_path, 'r') as gpx_file:
                gpx = gpxpy.parse(gpx_file)

            points = []
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        geoid = GeoidKarney("egm2008-5.pgm")
                        location = LatLon(point.latitude,point.longitude)
                        height = geoid(location)
                        points.append(Point(latitude=point.latitude,longitude=point.longitude,elevation=point.elevation-height))
            
            return points
        except Exception:
            raise

class ElevationAPI:
    API_URL = "https://valhalla1.openstreetmap.de/height"

    @classmethod
    def get_elevations(cls, points: list[Point]) -> list[Point]:
        if not points:
            return []

        requ = {"shape": []}
        for j in range(0, len(points)):
            requ["shape"].append({"lat": points[j].latitude, "lon": points[j].longitude})
        ok = False
        try:
            response = requests.post(cls.API_URL,json=requ)
            if response.ok:
                ok = True
        except requests.ConnectionError:
            pass
        if ok:
            response = json.loads(response.content)
            results = points
            for i in range(0, len(response["height"])):
                results[i].elevation = response["height"][i]
            return results
        else:
            print("data could not be retrieved")
            return []



class OpenElevationAPI:
    API_URL = "https://api.open-elevation.com/api/v1/lookup"

    @classmethod
    def get_elevations(cls, points: list[Point]) -> list[Point]:
        if not points:
            return []
        
        requ = {"locations": []}
        for j in range(0, len(points)):
            requ["locations"].append({"latitude": points[j].latitude, "longitude": points[j].longitude})
        ok = False
        try:
            response = requests.post(cls.API_URL, json=requ)
            if response.ok:
                ok = True
        except requests.ConnectionError:
            pass
        if ok:
            response = json.loads(response.content)
            results = points
            for i in range(0, len(response["results"])):
               results[i].elevation = response["results"][i]["elevation"]
            return results
        else:
            print("open-elevation data could not be retrieved")
            return []

class GeoCalculator:
    EARTH_RADIUS_KM = 6371.0

    @staticmethod
    def haversine_distance(point1: Point, point2: Point) -> float:
        lat1, lon1 = radians(point1.latitude), radians(point1.longitude)
        lat2, lon2 = radians(point2.latitude), radians(point2.longitude)

        d_lat = lat2 - lat1
        d_lon = lon2 - lon1

        a = sin(d_lat/2)**2 + cos(lat1)*cos(lat2)*sin(d_lon/2)**2
        c = 2*atan2(sqrt(a), sqrt(1-a))

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
            distance = GeoCalculator.haversine_distance(self.points[i-1], self.points[i])
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
    
class ElevationPlotter:

    @staticmethod
    def plot_comparison(
        profile1: ElevationProfile,
        profile2: ElevationProfile,
        label1: str = "GPX Elevation",
        label2: str = "Open-Elevation",
        title: str = "Elevation Profile Comparison"
    ):
        plt.figure(figsize=(12,6))

        plt.plot(
            profile1.get_distances(),
            profile1.get_elevations(),
            label = label1,
            color = 'blue',
            linewidth = 2
        )

        plt.plot(
            profile2.get_distances(),
            profile2.get_elevations(),
            label = label2,
            color = 'red',
            linestyle = '--',
            linewidth = 2
        )

        plt.title(title)
        plt.xlabel("Distance (km)")
        plt.ylabel("Elevation (m)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()


def main(gpx_file_path: str):
    try:
        gpx_points = GPXParser.parse_gpx_file(gpx_file_path)

        api_points = [Point(p.latitude, p.longitude) for p in gpx_points]
        api_points = OpenElevationAPI.get_elevations(api_points)
        api_2_points = ElevationAPI.get_elevations(api_points)

        gpx_profile = ElevationProfile(gpx_points)
        api_profile = ElevationProfile(api_points)
        api_2_profile = ElevationProfile(api_2_points)

        ElevationPlotter.plot_comparison(
            gpx_profile,
            api_profile,
            title=f"Elevation Profile Comparison\n{gpx_file_path}"
        )

        ElevationPlotter.plot_comparison(
            gpx_profile,
            api_2_profile,
            title=f"Elevation Profile Comparison, API 2\n{gpx_file_path}"
        )

        plt.figure(figsize=(12, 6))
        plt.plot(api_profile.get_distances(), api_profile.get_elevations(), label="API1", color="red")
        plt.plot(api_2_profile.get_distances(), api_2_profile.get_elevations(), label="API2", color="blue", linestyle="--")
        plt.show()
    except Exception:
        raise

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare GPX Elevation with API")
    parser.add_argument("gpx_file", help='Path to the GPX file')

    args = parser.parse_args()
    main(args.gpx_file)

