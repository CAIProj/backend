from models import Point
import requests
import json


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
            response = requests.post(cls.API_URL, json=requ)
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