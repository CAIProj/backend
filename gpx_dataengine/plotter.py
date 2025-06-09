import math

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.interpolate import griddata
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from elevationprofile import ElevationProfile, GeoCalculator
from gpxdata import GPXParser, Point
from elevationapi import OpenElevationAPI

#TODO: implement a variety of plots
#TODO: update labels on plots

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
        title: str = "Elevation Profile Comparison",
        tolerance_vector: list[bool] = None
    ):
        if tolerance_vector is not None:
            tolerance_vector = np.array(tolerance_vector)

            segments = []
            start = 0
            for i in range(1, len(tolerance_vector)):
                if tolerance_vector[i] != tolerance_vector[i-1]:
                    segments.append((start, i))
                    start = i
            segments.append((start, len(tolerance_vector)))

            plt.figure(figsize=(12,6))

            plt.plot(profile1.get_distances(),
                     profile1.get_elevations(),
                     label=label1,
                     color='black',
                     linewidth=2)

            for start, end in segments:
                if tolerance_vector[start]:
                    plt.plot(profile2.get_distances()[start:end],
                             profile2.get_elevations()[start:end],
                             color='green') #plot when gpx2 is within tolerance
                else:
                    plt.plot(profile2.get_distances()[start:end],
                             profile2.get_elevations()[start:end],
                             color='red',
                             linestyle='--') #plot when gpx2 is outside of tolerance

            plt.title(title)
            plt.xlabel("Distance (km)")
            plt.ylabel("Elevation (m)")
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()
        else:
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

    @staticmethod
    def start_sync(
            gpx1: list[Point],
            gpx2: list[Point],
            tolerance: float = 0.1
    ):
        START_THRESH = 20 #The number of points at the start of the file to consider to find a common starting point
        index1 = 0
        index2 = 0
        distance = float('inf')
        #index1 and index2 store the indices of the closest points in the start threshold in order to trim the files at the same point
        for i in range(min(START_THRESH, len(gpx1))):
            for j in range(min(START_THRESH, len(gpx2))):
                if GeoCalculator.haversine_distance(gpx1[i],gpx2[j]) < distance:
                    index1 = i
                    index2 = j
                    distance = GeoCalculator.haversine_distance(gpx1[i],gpx2[j])
        gpx1 = gpx1[index1:]
        gpx2 = gpx2[index2:]
        if distance > tolerance:
            print("No starting points found within tolerance")
            return None
        tolerance_vector = []
        vector_length = 0
        if len(gpx2) <= len(gpx1):
            vector_length = len(gpx2)
        else:
            vector_length = len(gpx1)
        for i in range(vector_length):
            if GeoCalculator.haversine_distance(gpx1[i], gpx2[i]) < tolerance:
                tolerance_vector.append(True)
            else:
                tolerance_vector.append(False)
        if len(tolerance_vector) < len(gpx2):
            tolerance_vector.extend([False]*(len(gpx2) - len(tolerance_vector)))

        gpx1_profile = ElevationProfile(gpx1)
        gpx2_profile = ElevationProfile(gpx2)
        return gpx1_profile, gpx2_profile, tolerance_vector

    #space_sync is an attempt to synchronise matching segments and discard non-matching segments, but was too complicated
    # @staticmethod
    # def space_sync(
    #         gpx1: list[Point],
    #         gpx2: list[Point],
    #         tolerance: int = 10
    # ):
    #
    #     start_point = min((i for i in range(len(gpx2))), key=lambda i: GeoCalculator.haversine_distance(gpx1[0], gpx2[i]))
    #     if GeoCalculator.haversine_distance(gpx1[0], gpx2[start_point]) > tolerance:
    #         print("There are no common coordinates between the two files, make sure the files represent the same route")
    #         raise ValueError
    #     new_gpx2 = gpx2[start_point:]
    #     if len(new_gpx2) < 3:
    #         print("There are not enough common coordinates between the two files, make sure the files represent the same route")
    #         raise ValueError
    #
    #     points_within_tolerance = [any(GeoCalculator.haversine_distance(a, b) < tolerance for a in gpx1) for b in new_gpx2]
    #     while points_within_tolerance[-1] == False:
    #         points_within_tolerance = points_within_tolerance[:-1]
    #         new_gpx2 = new_gpx2[:-1]
    #         # removes all points at the end of gpx2 that aren't close to any point in gpx1
    #
    #     gpx1_profile = ElevationProfile(gpx1)
    #     gpx2_profile = ElevationProfile(new_gpx2)
    #     gpx1_distances = gpx1_profile.get_distances()
    #
    #     for point in gpx1:
    #         segment = []
    #
    #     # TODO: find segments of gpx2 that are within range of segments of gpx1 and make those segments have the same
    #     # distances, once a point in gpx2 is no longer within range at the same point in gpx1, if the corresponding flag
    #     # in points_within_tolerance is True, then perhaps it matches up with a later segment of gpx1 so it can be the beginning
    #     # of a new segment, but if the flag is False, then it is completely out of range and set the elevation to None
    #     # so the plot will have a gap. We should also consider removing all points beyond that that have the False flag
    #     # to make things simpler as the beginning of the next segment should have the True flag.






def plot2d(args):
    gpx_file_1 = args.gpx1
    gpx_file_2 = args.gpx2

    try:
        gpx_points_1 = GPXParser.parse_gpx_file(gpx_file_1)
        gpx_points_2 = GPXParser.parse_gpx_file(gpx_file_2)

        gpx_profile_1, gpx_profile_2, tolerance_vector = ElevationPlotter.start_sync(gpx_points_1, gpx_points_2)

        ElevationPlotter.plot_comparison(gpx_profile_1, gpx_profile_2, tolerance_vector=tolerance_vector)

        # # truncate longer file
        # min_len = min(len(gpx_points_1), len(gpx_points_2))
        # gpx_points_1 = gpx_points_1[:min_len]
        # gpx_points_2 = gpx_points_2[:min_len]
        #
        # gpx_profile_1 = ElevationProfile(gpx_points_1)
        # gpx_profile_2 = ElevationProfile(gpx_points_2)
        #
        # ElevationPlotter.plot_comparison(gpx_profile_1, gpx_profile_2)
    except:
        raise
