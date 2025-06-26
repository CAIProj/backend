import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from models import ElevationProfile, Track
from elevation_api import OpenElevationAPI, OpenStreetMapElevationAPI


# Standalone comparison plot using both APIs
def compare_elevation_apis(gpx_file_path: str):
    from plotter import Plotter  # Delayed import to avoid circular dependency with plotter.py

    try:
        track = Track.from_gpx_file(gpx_file_path)

        # get track with api elevations
        openelevation_elevation_track = track.with_api_elevations(OpenElevationAPI)
        openstreetmap_elevation_track = track.with_api_elevations(OpenStreetMapElevationAPI)


        # Plot comparision plots
        plotter1 = Plotter()
        plotter1.add_profiles(
            (track.elevation_profile, 'From GPX file'),
            (openelevation_elevation_track.elevation_profile, 'From Openelevation API'),
        )
        plotter1.plot_distance_vs_elevation()
        
        plotter2 = Plotter()
        plotter2.add_profiles(
            (track.elevation_profile, 'From GPX file'),
            (openstreetmap_elevation_track.elevation_profile, 'From Openstreetmap API') 
        )
        plotter2.plot_distance_vs_elevation()
        
    except Exception as e:
        print(f"An error occurred during comparison: {e}")
        raise
    
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare elevation data from multiple APIs")
    parser.add_argument("gpx_file", help="Path to the GPX file to compare elevations")
    args = parser.parse_args()

    compare_elevation_apis(args.gpx_file)