from dataclasses import dataclass
from typing import Optional


@dataclass
class Point:
    "Represents a geographical point (log, lat, elevation)"
    latitude: float
    longitude: float
    elevation: Optional[float] = None

    def to_dict(self) -> dict:
        return {'latitude': self.latitude, 'longitude': self.longitude}