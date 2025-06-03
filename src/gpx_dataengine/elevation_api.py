from models import Point
import requests
import json
import matplotlib.pyplot as plt
from models import ElevationProfile, Track


class ElevationAPI:
    API_URL = "https://valhalla1.openstreetmap.de/height"

    @classmethod
    def get_elevations(cls, points: list[Point]) -> list[float]:
        """
        Returns a list of elevations for the given Points, in the same order.

        Args:
            points (list[Point]): List of Points representing geographical locations.

        Returns:
            list[float]: Elevations of the Points (in input order) if the API request is successful; otherwise, an empty list.
        """
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


class OpenElevationAPI:
    API_URL = "https://api.open-elevation.com/api/v1/lookup"

    @classmethod
    def get_elevations(cls, points: list[Point]) -> list[float]:
        """
        Returns a list of elevations for the given Point objects, in the same order.

        Args:
            points (list[Point]): List of Point objects representing geographical locations.

        Returns:
            list[float]: Elevations of the Point objects (in input order) if the API request is successful; otherwise, an empty list.
        """
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