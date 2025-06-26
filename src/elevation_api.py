from abc import ABC, abstractmethod
from .models import Point
import requests
import json


class BaseElevationAPI(ABC):
    @classmethod
    @abstractmethod
    def get_elevations(cls, points: list[Point]) -> list[float]:
        """
        Return a list of elevations for the given Points, in the same order.

        Args:
            points (list[Point]): List of Points representing geographical locations.

        Returns:
            list[float]: Elevations of the Points (in input order) if the API request is successful; otherwise, an empty list.
        """
        pass

class OpenStreetMapElevationAPI(BaseElevationAPI):
    API_URL = "https://valhalla1.openstreetmap.de/height"

    @classmethod
    def get_elevations(cls, points: list[Point]) -> list[float]:
        if not points:
            return []

        requ = {"shape": [{"lat": p.latitude, "lon": p.longitude} for p in points]}
        try:
            response = requests.post(cls.API_URL, json=requ)
            if response.ok:
                response_data = json.loads(response.content)
                return response_data["height"]
            else:
                print("API request failed: Data could not be retrieved")
                return []
        except requests.ConnectionError:
            print("Connection error: Data could not be retrieved")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []


class OpenElevationAPI(BaseElevationAPI):
    API_URL = "https://api.open-elevation.com/api/v1/lookup"

    @classmethod
    def get_elevations(cls, points: list[Point]) -> list[float]:
        if not points:
            return []

        requ = {"locations": [{"latitude": p.latitude, "longitude": p.longitude} for p in points]}
        try:
            response = requests.post(cls.API_URL, json=requ)
            if response.ok:
                response_data = json.loads(response.content)
                return [entry["elevation"] for entry in response_data["results"]]
            else:
                print("API request failed: open-elevation data could not be retrieved")
                return []
        except requests.ConnectionError:
            print("Connection error: open-elevation data could not be retrieved")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []