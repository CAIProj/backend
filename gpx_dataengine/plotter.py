import matplotlib.pyplot as plt
import scipy.spatial
import numpy as np
from scipy.interpolate import interp1d
from elevationprofile import ElevationProfile, GeoCalculator
from gpxdata import GPXParser, Point
from elevationapi import OpenElevationAPI
import bisect


class Plot3D:
    """
    This class holds all the methods needed for 3D plotting
    """
    @staticmethod
    def plot_comparison(
            profile1: ElevationProfile,
            profile2: ElevationProfile,
            label1: str = "Base Plot",
            label2: str = "Comparison Plot",
            title: str = "3D Plot of 2 GPX Files",
            output: str = None
    ):
        """
        This method is used to compare two gpx files in a 3d plot
        :param profile1: Required. This is the first gpx file in an ElevationProfile object
        :param profile2: Required. This is the second gpx file in an ElevationProfile object
        :param label1: Optional. This is the label for profile1
        :param label2: Optional. This is the label for profile2
        :param title: Optional. This is the title of the plot
        :param output: Optional. This is the output path for the plot if you want to save it instead of displying it
        :return: n/a
        """
        fig = plt.figure()
        ax = fig.add_subplot(111,projection="3d")

        ax.plot(profile1.get_latitudes(), profile1.get_longitudes(), profile1.get_elevations(),
                label=label1, color='blue', linewidth=1.5)

        ax.plot(profile2.get_latitudes(), profile2.get_longitudes(), profile2.get_elevations(),
                label=label2, color='red', linewidth=1.5)

        ax.set_title(title)
        ax.set_xlabel('Latitude')
        ax.set_ylabel('Longitude')
        ax.set_zlabel('Elevation (m)')
        ax.legend()
        plt.tight_layout()
        if output:
            plt.savefig(output)
        else:
            plt.show()

def plot3d(main_args):
    """
    This method is called from main.py if a 3d plot is desired
    :param main_args: arguments passed from the command line
    :return:
    """
    file1 = main_args.base_gpx
    file2 = main_args.gpx2

    output = main_args.output if main_args.output else None
    #output contains a file path to save the plot, if None it will display the plot on screen

    try:
        gpx_points_1 = GPXParser.parse_gpx_file(file1)
        gpx_points_2 = GPXParser.parse_gpx_file(file2)

        gpx_profile_1 = ElevationProfile(gpx_points_1)
        gpx_profile_2 = ElevationProfile(gpx_points_2)

        #if a custom title is passed from the command line, then it is passed to the plotter
        if main_args.title:
            Plot3D.plot_comparison(
                gpx_profile_1,
                gpx_profile_2,
                title=main_args.title,
                output=output
            )
        else:
            Plot3D.plot_comparison(
                gpx_profile_1,
                gpx_profile_2,
                output=output
            )

    except:
        raise


class ElevationPlotter:
    """
    This class contains all the methods needed for a 2D elevation plot
    """

    @staticmethod
    def plot_comparison(
        profile1: ElevationProfile,
        profile2: ElevationProfile,
        label1: str = "Base Plot",
        label2: str = "Comparison Plot",
        title: str = "Elevation Profile Comparison",
        tolerance_vector: list[bool] = None,
        output: str = None
    ):
        """
        This function plots the elevation of two gpx files, or a single gpx file and elevation data from an API
        :param profile1: Required. This is the base gpx file on which the second file will be compared
        :param profile2: Required. This is the gpx file or API elevation data being compared to the base file
        :param label1: Optional. This is the label for profile1
        :param label2: Optional. This is the label for profile2
        :param title: Optional. This is the title of the plot
        :param tolerance_vector: Optional. If a tolerance vector is passed, it will modify profile2 to show how close it is to the profile1
        :param output: Optional. The output path if you want to save the plot rather than show it on screen
        :return:
        """
        if tolerance_vector is not None: #logic for producing a plot that displays where the comparison track diverges from the base track
            tolerance_vector = np.array(tolerance_vector)

            #segment the tolerance vector into groups of all True and all False
            segments = []
            start = 1
            for i in range(1, len(tolerance_vector)):
                if tolerance_vector[i] != tolerance_vector[i-1]:
                    segments.append((start - 1, i))
                    start = i
            segments.append((start, len(tolerance_vector)))

            plt.figure(figsize=(12,6))

            plt.plot(profile1.get_distances(),
                     profile1.get_elevations(),
                     label=label1,
                     color='black',
                     linewidth=2)

            #plots True segments in green and False segments in red
            for start, end in segments:
                if tolerance_vector[start]:
                    plt.plot(profile2.get_distances()[start:end],
                             profile2.get_elevations()[start:end],
                             color='green') #plot when gpx2 is within tolerance
                else:
                    plt.plot(profile2.get_distances()[start:end],
                             profile2.get_elevations()[start:end],
                             color='red') #plot when gpx2 is outside of tolerance

            plt.title(title)
            plt.xlabel("Distance (km)")
            plt.ylabel("Elevation (m)")
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            if output:
                plt.savefig(output)
            else:
                plt.show()
        else: #logic for plots without a tolerance vector
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
                linewidth = 2
            )

            plt.title(title)
            plt.xlabel("Distance (km)")
            plt.ylabel("Elevation (m)")
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            if output:
                plt.savefig(output)
            else:
                plt.show()

    @staticmethod
    def get_tolerance_vector(
            profile1: ElevationProfile,
            profile2: ElevationProfile,
            tolerance: float) -> list[bool]:
        """
        This is the standard method of producing a tolerance vector. It iterates over the points in the comparison profile
        and compares it to the corresponding points either side of it in the base profile to see which is closer before
        checking the tolerance.
        :param profile1: Required. ElevationProfile for the base track
        :param profile2: Required. ElevationProfile for the comparison track
        :param tolerance: Required. Tolerance range (km)
        :return: tolerance vector
        """
        n = len(profile2.points)
        tolerance_vector = [False] * n

        if not profile1.distances or not profile1.points:
            return tolerance_vector

        dists1 = profile1.distances
        max_dist = dists1[-1]

        for i in range(n):
            d2 = profile2.distances[i]
            if d2 < 0 or d2 > max_dist:
                continue

            pos = bisect.bisect_left(dists1, d2)
            candidates = []
            if pos > 0:
                candidates.append(pos-1)
            if pos < len(dists1):
                candidates.append(pos)

            best_j = candidates[0]
            best_diff = abs(dists1[best_j] - d2)
            for j in candidates[1:]:
                diff = abs(dists1[j] - d2)
                if diff < best_diff:
                    best_j = j
                    best_diff = diff

            if GeoCalculator.haversine_distance(profile1.points[best_j], profile2.points[i]) <= tolerance:
                tolerance_vector[i] = True

        return tolerance_vector

    @staticmethod
    def kdtree_tolerance(
            profile1: ElevationProfile,
            profile2: ElevationProfile,
            tolerance: float
    ):
        """
        This is an alternative method of calculating the tolerance vector by using a k-d tree to see if each point in
        the comparison profile is within tolerance of any point within profile2
        :param profile1: Required. ElevationProfile for base track
        :param profile2: Required. ElevationProfile for comparison track
        :param tolerance: Required. Tolerance range (km)
        :return: tolerance vector
        """
        def latlon_to_cartesian(lat, lon, radius=6371.0):
            #This method is used to convert latitude and longitude to cartesian coordinate for the k-d tree
            lat = np.radians(lat)
            lon = np.radians(lon)
            x = radius * np.cos(lat) * np.cos(lon)
            y = radius * np.cos(lat) * np.sin(lon)
            z = radius * np.sin(lat)
            return np.vstack((x, y, z)).T

        lats1 = np.array([p.latitude for p in profile1.points])
        lons1 = np.array([p.longitude for p in profile1.points])
        xyz1 = latlon_to_cartesian(lats1, lons1)

        lats2 = np.array([p.latitude for p in profile2.points])
        lons2 = np.array([p.longitude for p in profile2.points])
        xyz2 = latlon_to_cartesian(lats2, lons2)

        tree = scipy.spatial.KDTree(xyz1)

        points_within_tolerance = tree.query_ball_point(xyz2, tolerance) #checks which points every point in the comparison track is within tolerance of any point within the base track

        matching_points = np.array([len(m) > 0 for m in points_within_tolerance]) #converts points_within_tolerance to a boolean vector

        return matching_points


    @staticmethod
    def elevation_sync(
            gpx1: list[Point],
            gpx2: list[Point],
            tolerance: float = 0.1,
            tolerance_method: str = "standard"
    ):
        """
        This is a synchronisation method to shift the comparison plot to a position where the elevation plots best match
        :param gpx1: Required. Base gpx file, parsed
        :param gpx2: Required. Comparison gpx file, parsed
        :param tolerance: Optional. Tolerance range (km)
        :param tolerance_method: Optional. Which method should be used to calculate the tolerance vector
        :return: ElevationProfile, ElevationProfile, tolerance vector
        """
        gpx1_profile = ElevationProfile(gpx1)
        gpx2_profile = ElevationProfile(gpx2)

        profile1_interp = interp1d(gpx1_profile.distances, [p.elevation for p in gpx1_profile.points], fill_value="extrapolate")
        profile2_interp = interp1d(gpx2_profile.distances, [p.elevation for p in gpx2_profile.points],
                                   fill_value="extrapolate")

        min_dist = max(min(gpx1_profile.distances), min(gpx2_profile.distances))
        max_dist = min(max(gpx1_profile.distances), max(gpx2_profile.distances))
        common_distances = np.linspace(min_dist, max_dist, 1000)

        elevs1 = profile1_interp(common_distances)
        elevs2 = profile2_interp(common_distances)

        max_shift_samples = 50
        errors = []

        for shift in range(-max_shift_samples, max_shift_samples + 1):
            if shift < 0:
                shifted = elevs2[-shift:]
                reference = elevs1[:len(shifted)]
            elif shift > 0:
                shifted = elevs2[:-shift]
                reference = elevs1[shift:]
            else:
                shifted = elevs2
                reference = elevs1
            error = np.mean((np.array(shifted) - np.array(reference))**2)
            errors.append(error)

        best_shift_index = np.argmin(errors) - max_shift_samples
        step_size = (max_dist - min_dist) / len(common_distances)
        best_shift_distance = best_shift_index * step_size

        gpx2_profile.set_distances([d + best_shift_distance for d in gpx2_profile.distances])

        if tolerance_method == "standard":
            return gpx1_profile, gpx2_profile, ElevationPlotter.get_tolerance_vector(gpx1_profile, gpx2_profile, tolerance)
        else:
            return gpx1_profile, gpx2_profile, ElevationPlotter.kdtree_tolerance(gpx1_profile, gpx2_profile, tolerance)


    @staticmethod
    def start_sync(
            gpx1: list[Point],
            gpx2: list[Point],
            tolerance: float = 0.1,
            tolerance_method: str = "standard"
    ):
        """
        This is a synchronisation method to trim the start of each gpx file to a position where they start at the closest point
        :param gpx1: Required. Base gpx file, parsed
        :param gpx2: Required. Comparison gpx file, parsed
        :param tolerance: Optional. Tolerance range (km)
        :param tolerance_method: Optional. Which method should be used to calculate the tolerance vector
        :return: ElevationProfile, ElevationProfile, tolerance vector
        """
        START_THRESH = 50 #The number of points at the start of the file to consider to find a common starting point
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

        gpx1_profile = ElevationProfile(gpx1)
        gpx2_profile = ElevationProfile(gpx2)
        if tolerance_method == "standard":
            return gpx1_profile, gpx2_profile, ElevationPlotter.get_tolerance_vector(gpx1_profile, gpx2_profile, tolerance)
        else:
            return gpx1_profile, gpx2_profile, ElevationPlotter.kdtree_tolerance(gpx1_profile, gpx2_profile, tolerance)

    @staticmethod
    def interpolate_elevations(
            gpx1: list[Point],
            gpx2: list[Point],
            tolerance: float = 0.1,
            tolerance_method: str = "standard"
    ):
        """
        This is a synchronisation method to plot the comparison track at the same intervals as the base track
        by interpolating the measured elevations
        :param gpx1: Required. Base gpx file, parsed
        :param gpx2: Required. Comparison gpx file, parsed
        :param tolerance: Optional. Tolerance range (km)
        :param tolerance_method: Optional. Which method should be used to calculate the tolerance vector
        :return: ElevationProfile, ElevationProfile, tolerance vector
        """
        gpx1_profile = ElevationProfile(gpx1)
        gpx2_profile = ElevationProfile(gpx2)

        gpx2_distances = gpx2_profile.get_distances()
        gpx2_elevations = gpx2_profile.get_elevations()

        new_elevations = []

        for d in gpx1_profile.distances:
            if d <= gpx2_distances[0]:
                new_elevations.append(gpx2_elevations[0])
            elif d >= gpx2_distances[-1]:
                new_elevations.append(gpx2_elevations[-1])
            else:
                idx = bisect.bisect_left(gpx2_distances, d)
                left_idx = idx - 1
                right_idx = idx

                dist_left = gpx2_distances[left_idx]
                dist_right = gpx2_distances[right_idx]
                elev_left = gpx2_elevations[left_idx]
                elev_right = gpx2_elevations[right_idx]

                if dist_left == dist_right:
                    new_elevations.append(elev_left)
                else:
                    ratio = (d - dist_left) / (dist_right - dist_left)
                    interp_elev = elev_left + ratio * (elev_right - elev_left)
                    new_elevations.append(interp_elev)

        gpx2_profile = ElevationProfile(gpx2[:len(gpx1)])
        gpx2_profile.set_distances(gpx1_profile.get_distances())
        gpx2_profile.set_elevations(new_elevations)

        if tolerance_method == "standard":
            return gpx1_profile, gpx2_profile, ElevationPlotter.get_tolerance_vector(gpx1_profile, gpx2_profile, tolerance)
        else:
            return gpx1_profile, gpx2_profile, ElevationPlotter.kdtree_tolerance(gpx1_profile, gpx2_profile, tolerance)


def plot2d(args):
    """
    This method is called from main.py if a 2d elevation plot is desired
    :param args: arguments passed from the command line
    :return:
    """
    gpx_file_1 = args.base_gpx
    gpx_points_1 = GPXParser.parse_gpx_file(gpx_file_1)

    try:
        # create a comparison track from API data if "use-api" option is passed
        if args.use_api:
            gpx_points_2 = [Point(p.latitude, p.longitude) for p in gpx_points_1]
            gpx_points_2 = OpenElevationAPI.get_elevations(gpx_points_2)
        else:
            gpx_file_2 = args.gpx2
            gpx_points_2 = GPXParser.parse_gpx_file(gpx_file_2)

        output = args.output if args.output else None

        if args.tolerance: #tolerance is optional so plotter arguments will differ based on if it is enabled or not
            if args.sync_method == "elevation_sync":
                gpx_profile_1, gpx_profile_2, tolerance_vector = ElevationPlotter.elevation_sync(gpx_points_1, gpx_points_2,
                                                                                                 args.tolerance, args.tolerance_method)
            elif args.sync_method == "start_sync":
                gpx_profile_1, gpx_profile_2, tolerance_vector = ElevationPlotter.start_sync(gpx_points_1, gpx_points_2,
                                                                                             args.tolerance, args.tolerance_method)
            elif args.sync_method == "interpolate_elevations":
                gpx_profile_1, gpx_profile_2, tolerance_vector = ElevationPlotter.interpolate_elevations(gpx_points_1,
                                                                                                         gpx_points_2,
                                                                                                         args.tolerance,
                                                                                                         args.tolerance_method)
            else:
                raise
            if args.title:
                ElevationPlotter.plot_comparison(gpx_profile_1, gpx_profile_2, tolerance_vector=tolerance_vector,
                                                 title=args.title, output=output)
            else:
                ElevationPlotter.plot_comparison(gpx_profile_1, gpx_profile_2, tolerance_vector=tolerance_vector, output=output)
        else:
            if args.sync_method == "elevation_sync":
                gpx_profile_1, gpx_profile_2, _ = ElevationPlotter.elevation_sync(gpx_points_1, gpx_points_2)
            elif args.sync_method == "start_sync":
                gpx_profile_1, gpx_profile_2, _ = ElevationPlotter.start_sync(gpx_points_1, gpx_points_2)
            elif args.sync_method == "interpolate_elevations":
                gpx_profile_1, gpx_profile_2, _ = ElevationPlotter.interpolate_elevations(gpx_points_1, gpx_points_2)
            else:
                raise
            if args.title:
                ElevationPlotter.plot_comparison(gpx_profile_1, gpx_profile_2, title=args.title, output=output)
            else:
                ElevationPlotter.plot_comparison(gpx_profile_1, gpx_profile_2, output=output)

    except:
        raise

class SurfacePlot:
    """
    This class contains the methods needed for a 2d surface (lat, lon) plot
    """
    @staticmethod
    def plot_comparison(
            gpx1: list[Point],
            gpx2: list[Point],
            label1: str = "Base Route",
            label2: str = "Comparison Route",
            title: str = "Surface Route Comparison",
            output: str = None
    ):
        """
        This method is used to plot two tracks for comparison
        :param gpx1: Required. The first route to be plotted
        :param gpx2: Required. The second route to be plotted
        :param label1: Optional. The label for the first route
        :param label2: Optional. The label for the second route
        :param title: Optional. The title for the plot
        :param output: Optional. The file path to save the plot, if None it will display the plot
        :return:
        """
        plt.figure(figsize=(12, 6))

        plt.plot(
            [p.latitude for p in gpx1],
            [p.longitude for p in gpx1],
            label=label1,
            color='blue',
            linewidth=2
        )

        plt.plot(
            [p.latitude for p in gpx2],
            [p.longitude for p in gpx2],
            label=label2,
            color='red',
            linewidth=2,
            alpha = 0.7
        )

        plt.title(title)
        plt.xlabel("Latitude")
        plt.ylabel("Longitude")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        if output:
            plt.savefig(output)
        else:
            plt.show()

    @staticmethod
    def plot_single(
            gpx1: list[Point],
            label: str = "Route",
            title: str = "Route Plot",
            output: str = None
    ):
        """
        This method is to plot a single track
        :param gpx1: Required. The (parsed) gpx file to be plotted
        :param label: Optional. The label for the plot
        :param title: Optional. The title for the plot
        :param output: Optional. The file path to save the plot, if None it will only display the plot
        :return:
        """
        plt.figure(figsize=(12,6))

        plt.plot(
            [p.latitude for p in gpx1],
            [p. longitude for p in gpx1],
            label=label,
            color='black',
            linewidth=2
        )

        plt.title(title)
        plt.xlabel("Latitude")
        plt.ylabel("Longitude")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        if output:
            plt.savefig(output)
        else:
            plt.show()

def plot_surface(args):
    """
    This method is called from main.py if a 2d surface plot is desired
    :param args: arguments passed from the command line
    :return:
    """
    gpx1 = args.base_gpx
    gpx1_points = GPXParser.parse_gpx_file(gpx1)

    try:
        output = args.output if args.output else None
        if args.use_api or args.gpx2:
            if args.use_api:
                gpx2_points = [Point(p.latitude, p.longitude) for p in gpx1_points]
                gpx2_points = OpenElevationAPI.get_elevations(gpx2_points)
            else:
                gpx_file_2 = args.gpx2
                gpx2_points = GPXParser.parse_gpx_file(gpx_file_2)
            if args.title:
                SurfacePlot.plot_comparison(gpx1_points, gpx2_points, title=args.title, output=output)
            else:
                SurfacePlot.plot_comparison(gpx1_points, gpx2_points, output=output)
        else:
            if args.title:
                SurfacePlot.plot_single(gpx1_points, title=args.title, output=output)
            else:
                SurfacePlot.plot_single(gpx1_points, output=output)
    except:
        raise


