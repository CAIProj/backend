import argparse
from .models import Track
from .elevation_api import OpenElevationAPI, OpenStreetMapElevationAPI

def compare_elevation_apis(gpx_file_path: str, use_openelevation: bool, use_openstreetmap: bool):
    """
    Compare elevation profiles from the GPX file and selected elevation APIs.

    Args:
        gpx_file_path (str): Path to the GPX file.
        use_openelevation (bool): Whether to include data from OpenElevation API.
        use_openstreetmap (bool): Whether to include data from OpenStreetMap API.
    """
    from plotter import Plotter  # Delayed import to avoid circular dependency with plotter.py

    try:
        track = Track.from_gpx_file(gpx_file_path)
        profiles_to_plot = [(track.elevation_profile, "From GPX file")]

        if use_openelevation:
            oe_track = track.with_api_elevations(OpenElevationAPI)
            profiles_to_plot.append((oe_track.elevation_profile, "From OpenElevation API"))

        if use_openstreetmap:
            osm_track = track.with_api_elevations(OpenStreetMapElevationAPI)
            profiles_to_plot.append((osm_track.elevation_profile, "From OpenStreetMap API"))

        plotter = Plotter()
        plotter.add_profiles(*profiles_to_plot)
        plotter.plot_distance_vs_elevation()

    except Exception as e:
        print(f"An error occurred during comparison: {e}")
        raise
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare elevation data from a GPX file and selected APIs")
    parser.add_argument("gpx_file", help="Path to the GPX file")
    parser.add_argument("--openelevation", action="store_true", help="Include elevation data from OpenElevation API")
    parser.add_argument("--openstreetmap", action="store_true", help="Include elevation data from OpenStreetMap API")

    args = parser.parse_args()

    # If no API flags are set, include both by default
    if not args.openelevation and not args.openstreetmap:
        args.openelevation = args.openstreetmap = True

    compare_elevation_apis(
        gpx_file_path=args.gpx_file,
        use_openelevation=args.openelevation,
        use_openstreetmap=args.openstreetmap
    )
