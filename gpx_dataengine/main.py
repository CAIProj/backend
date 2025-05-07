from gpxdata import GPXParser, Point
from elevationapi import OpenElevationAPI, ElevationAPI
from elevationprofile import ElevationProfile
from plotter import ElevationPlotter
import matplotlib.pyplot as plt

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

