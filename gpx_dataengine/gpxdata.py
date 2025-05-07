from pygeodesy import GeoidKarney
from pygeodesy.ellipsoidalKarney import LatLon
from typing import Optional
import gpxpy
import gpxpy.gpx
from dataclasses import dataclass

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
                        location = LatLon(point.latitude, point.longitude)
                        height = geoid(location)
                        points.append(Point(latitude=point.latitude, longitude=point.longitude,
                                            elevation=point.elevation - height))

            return points
        except Exception:
            raise