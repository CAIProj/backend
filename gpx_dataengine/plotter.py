import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.interpolate import griddata
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from elevationprofile import ElevationProfile
from gpxdata import GPXParser, Point
from elevationapi import OpenElevationAPI

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

def main(main_args):
    file1 = main_args.gpx_file_1
    file2 = main_args.gpx_file_2

    try:
        gpx_points_1 = GPXParser.parse_gpx_file(file1)
        gpx_points_2 = GPXParser.parse_gpx_file(file2)

        #truncate longer file
        min_len = min(len(gpx_points_1),len(gpx_points_2))
        gpx_points_1 = gpx_points_1[:min_len]
        gpx_points_2 = gpx_points_2[:min_len]

        api_points_1 = [Point(p.latitude, p.longitude) for p in gpx_points_1]
        api_points_1 = OpenElevationAPI.get_elevations(api_points_1)

        api_points_2 = [Point(p.latitude, p.longitude) for p in gpx_points_2]
        api_points_2 = OpenElevationAPI.get_elevations(api_points_2)

        gpx_profile_1 = ElevationProfile(gpx_points_1)
        gpx_profile_2 = ElevationProfile(gpx_points_2)
        api_profile_1 = ElevationProfile(api_points_1)
        api_profile_2 = ElevationProfile(api_points_2)

        Plot3D.plot_comparison(
            gpx_profile_1,
            gpx_profile_2,
            api_profile_1,
            api_profile_2
        )
    except:
        raise


class ElevationPlotter:

    @staticmethod
    def plot_comparison(
        profile1: ElevationProfile,
        profile2: ElevationProfile,
        label1: str = "GPX Elevation",
        label2: str = "Open-Elevation",
        title: str = "Elevation Profile Comparison"
    ):
        plt.figure(figsize=(12,6))

        plt.plot(
            profile1.get_distances(),
            profile1.get_elevations(),
            label = label1,
            color = 'blue',
            linewidth = 2
        )

        plt.plot(
            profile2.get_distances(),
            profile2.get_elevations(),
            label = label2,
            color = 'red',
            linestyle = '--',
            linewidth = 2
        )

        plt.title(title)
        plt.xlabel("Distance (km)")
        plt.ylabel("Elevation (m)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare 2 GPX-files Elevation with API")
    parser.add_argument("gpx_file_1", help='Path to the first GPX file')
    parser.add_argument("gpx_file_2", help="Path to the second GPX file")
    parser.add_argument("mode", default="3d", choices=["3d"], help="What type of plot?: 3d,...")

    args = parser.parse_args()
    main(args)