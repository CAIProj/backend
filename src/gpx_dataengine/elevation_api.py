from models import Point
import requests
import json
import matplotlib.pyplot as plt
from models import ElevationProfile, Track


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


# Standalone comparison plot using both APIs
def compare_elevation_apis(gpx_file_path: str):
    from plotter import ElevationPlotter  # Delayed import to avoid circular dependency with plotter.py

    try:
        track = Track.from_gpx_file(gpx_file_path)

        track_points_lat_long = [Point(p.latitude, p.longitude) for p in track.points]

        api_points_1 = OpenElevationAPI.get_elevations(track_points_lat_long.copy())
        api_profile_1 = ElevationProfile(api_points_1)

        api_points_2 = ElevationAPI.get_elevations(track_points_lat_long.copy())
        api_profile_2 = ElevationProfile(api_points_2)

        ElevationPlotter.plot_comparison(
            track.elevation_profile,
            api_profile_1,
            title=f"Elevation Profile Comparison (OpenElevationAPI)\n{gpx_file_path}"
        )

        ElevationPlotter.plot_comparison(
            track.elevation_profile,
            api_profile_2,
            title=f"Elevation Profile Comparison (ElevationAPI)\n{gpx_file_path}"
        )

        plt.figure(figsize=(12, 6))
        plt.plot(api_profile_1.get_distances(), api_profile_1.get_elevations(), label="OpenElevationAPI", color="red")
        plt.plot(api_profile_2.get_distances(), api_profile_2.get_elevations(), label="ElevationAPI", color="blue", linestyle="--")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.title("OpenElevationAPI vs ElevationAPI")
        plt.xlabel("Distance (km)")
        plt.ylabel("Elevation (m)")
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"An error occurred during comparison: {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare elevation data from multiple APIs")
    parser.add_argument("gpx_file", help="Path to the GPX file to compare elevations")
    args = parser.parse_args()

    compare_elevation_apis(args.gpx_file)