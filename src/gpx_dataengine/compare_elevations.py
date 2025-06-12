import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from models import ElevationProfile, Track
from elevation_api import OpenElevationAPI

class Plot3D:

    @staticmethod
    def plot_comparison(
            profile1: ElevationProfile,
            profile2: ElevationProfile,
            api_profile1: ElevationProfile,
            api_profile2: ElevationProfile,
            label1: str = "GPX 1 Plot",
            label2: str = "GPX 2 Plot",
            label3: str = "True Elevation for GPX 1",
            label4: str = "True Elevation for GPX 2",
            title: str = "3D Plot of 2 GPX Files"
    ):
        error_1 = np.array(profile1.get_elevations()) - np.array(api_profile1.get_elevations())
        error_2 = np.array(profile2.get_elevations()) - np.array(api_profile2.get_elevations())

        all_lat = np.concatenate([np.array(profile1.get_latitudes()), np.array(profile2.get_latitudes())])
        all_lon = np.concatenate([np.array(profile1.get_longitudes()), np.array(profile2.get_longitudes())])
        grid_lat, grid_lon = np.meshgrid(
            np.linspace(all_lat.min(), all_lat.max(), 100),
            np.linspace(all_lon.min(), all_lon.max(), 100)
        )

        combined_errors = np.concatenate([error_1, error_2])
        norm = Normalize(vmin=np.nanmin(combined_errors), vmax=np.nanmax(combined_errors))
        cmap = plt.cm.seismic

        min_elev = min(np.min(profile1.get_elevations()), np.min(profile2.get_elevations()),
                       np.min(api_profile1.get_elevations()), np.min(api_profile2.get_elevations()))
        heatmap_z = min_elev - 1

        grid_error1 = griddata((profile1.get_latitudes(), profile1.get_longitudes()), error_1, (grid_lat, grid_lon), method='cubic')
        grid_error2 = griddata((profile2.get_latitudes(), profile2.get_longitudes()), error_2, (grid_lat, grid_lon), method='cubic')

        grid_error1 = np.nan_to_num(grid_error1, nan=0)
        grid_error2 = np.nan_to_num(grid_error2, nan=0)

        fig = plt.figure()
        ax = fig.add_subplot(111,projection="3d")

        ax.plot_surface(grid_lat, grid_lon, np.full_like(grid_error1, heatmap_z),
                        facecolors=cmap(norm(grid_error1)),
                        rstride=1, cstride=1, alpha=0.5, shade=False)

        ax.plot_surface(grid_lat, grid_lon, np.full_like(grid_error2, heatmap_z),
                        facecolors=cmap(norm(grid_error2)),
                        rstride=1, cstride=1, alpha=0.5, shade=False)

        ax.plot(profile1.get_latitudes(), profile1.get_longitudes(), profile1.get_elevations(),
                label=label1, color='blue', linewidth=1.5)

        ax.plot(profile2.get_latitudes(), profile2.get_longitudes(), profile2.get_elevations(),
                label=label2, color='red', linewidth=1.5)

        ax.plot(api_profile1.get_latitudes(),api_profile1.get_longitudes(), api_profile2.get_elevations(),
                label=label3, color='orange', linestyle='--', linewidth=1.5)

        ax.plot(api_profile2.get_latitudes(), api_profile2.get_longitudes(), api_profile2.get_elevations(),
                label=label4, color='green', linestyle='--', linewidth=1.5)

        mappable = ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array(combined_errors)
        fig.colorbar(mappable, ax=ax, shrink=0.5, aspect=10, label='Elevation Error (m)')

        ax.set_title(title)
        ax.set_xlabel('Latitude')
        ax.set_ylabel('Longitude')
        ax.set_zlabel('Elevation (m)')
        ax.legend()
        plt.tight_layout()
        plt.show()

def plot3d(main_args):
    file1 = main_args.gpx1
    file2 = main_args.gpx2

    try:
        track_1 = Track.from_gpx_file(file1)
        track_2 = Track.from_gpx_file(file2)

        # Truncate longer file
        min_len = min(len(track_1.points), len(track_2.points))
        track_1.points = track_1.points[:min_len]
        track_2.points = track_2.points[:min_len]

        # Create profiles for evelvations from api
        elevations_from_openelevation_1 = OpenElevationAPI.get_elevations(track_1.points)
        elevation_profile_1 = track_1.elevation_profile.copy()
        elevation_profile_1.set_elevations(elevations_from_openelevation_1)

        elevations_from_openelevation_2 = OpenElevationAPI.get_elevations(track_2.points)
        elevation_profile_2 = track_2.elevation_profile.copy()
        elevation_profile_2.set_elevations(elevations_from_openelevation_2)


        # Plot the comparison plot
        Plot3D.plot_comparison(
            track_1.elevation_profile,
            track_2.elevation_profile,
            elevation_profile_1,
            elevation_profile_2,
        )
    except:
        raise