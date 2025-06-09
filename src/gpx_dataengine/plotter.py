import matplotlib.pyplot as plt
from models import ElevationProfile, Track, Point
from typing import Optional, List, Union, Tuple, Dict
import numpy as np

class Plotter:
    def __init__(self, profiles: Optional[List[Union[ElevationProfile, Tuple[ElevationProfile, str]]]] = None) -> None:
        """
        Initialize the Plotter with an optional list of ElevationProfile instances or (ElevationProfile, name) tuples.

        Args:
            profiles (Optional[List[Union[ElevationProfile, Tuple[ElevationProfile, str]]]]): 
                List of ElevationProfile instances or (ElevationProfile, name) tuples. 
                Defaults to None.
        """
        self.profiles: Dict[str, ElevationProfile] = {}
        if profiles:
            self.add_profiles(*profiles)

    def _generate_unique_name(self) -> str:
        """
        Generate a unique name like 'Profile 1', 'Profile 2', etc.

        Returns:
            str: Generated unique name.
        """
        idx = 1
        while f"Profile {idx}" in self.profiles:
            idx += 1
        return f"Profile {idx}"

    def add_profiles(
            self, 
            *profiles_with_names: Union[
                ElevationProfile, 
                Tuple[ElevationProfile, Optional[str]]
            ]
        ) -> None:
        """
        Add one or more ElevationProfile instances with optional names.

        Args:
            *profiles_with_names (Union[ElevationProfile, Tuple[ElevationProfile, Optional[str]]]): One or more ElevationProfile instances or 
                (ElevationProfile, name) tuples.

        Raises:
            ValueError: If the provided input is not valid.

        Examples:
            >>> plotter.add_profiles(profile)  # Auto-named
            >>> plotter.add_profiles((profile, "Hike"))
            >>> plotter.add_profiles((profile1, "Morning"), (profile2, "Evening"))
        """
        for item in profiles_with_names:
            if isinstance(item, ElevationProfile):
                # No name provided, auto-generate
                name = self._generate_unique_name()
                self.profiles[name] = item
            elif isinstance(item, tuple) and isinstance(item[0], ElevationProfile):
                profile = item[0]
                name = item[1] if item[1] else self._generate_unique_name()
                self.profiles[name] = profile
            else:
                raise ValueError("Provide either ElevationProfile or (ElevationProfile, name) tuples.")

    def set_profiles(self, profiles_dict: Dict[str, ElevationProfile]) -> None:
        """
        Replace all existing profiles with the given dictionary of profiles.

        Args:
            profiles_dict (Dict[str, ElevationProfile]): 
                Dictionary mapping names to ElevationProfile instances. 
                If the name is empty or invalid, a unique name will be generated.

        Raises:
            TypeError: If profiles_dict is not a dictionary.
            ValueError: If any profile is not an ElevationProfile instance.
        """
        if not isinstance(profiles_dict, dict):
            raise TypeError("Profiles must be provided as a dictionary {name: ElevationProfile}.")

        # Clear current profiles
        self.profiles = {}

        # Add each profile one by one using add_profiles
        for name, profile in profiles_dict.items():
            if not isinstance(profile, ElevationProfile):
                raise ValueError(f"Invalid profile for {name!r}: must be an ElevationProfile.")
            # If name is None/empty, let add_profiles auto-generate
            if not name or not isinstance(name, str) or name.strip() == "":
                self.add_profiles(profile)  # Auto-generate name
            else:
                self.add_profiles((profile, name.strip()))
    
    def plot_distance_vs_elevation(
        self,
        title: str = "Elevation Comparison",
        xlabel: str = "Distance (km)",
        ylabel: str = "Elevation (m)"
    ) -> None:
        """
        Plot elevation vs distance for all stored profiles.

        Args:
            title (str, optional): Title of the plot. Defaults to "Elevation Profiles Comparison".
            xlabel (str, optional): Label for the x-axis. Defaults to "Distance (km)".
            ylabel (str, optional): Label for the y-axis. Defaults to "Elevation (m)".
        """
        if not self.profiles:
            print("No profiles to plot.")
            return

        plt.figure(figsize=(12, 6))
        for name, profile in self.profiles.items():
            plt.plot(
                profile.get_distances(),
                profile.get_elevations(),
                label=name,
                linewidth=2
            )

        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
    
    def plot_3d_lat_lon_elevation(
        self,
        title: str = "3D Plot of Elevation Profiles",
        xlabel: str = "Latitude",
        ylabel: str = "Longitude",
        zlabel: str = "Elevation (m)"
    ) -> None:
        """
        Plot 3D trajectories of stored elevation profiles using latitude, longitude, and elevation.

        Args:
            title (str, optional): Title for the plot. Defaults to "3D Plot of Elevation Profiles".
            xlabel (str, optional): Label for the x-axis. Defaults to "Latitude".
            ylabel (str, optional): Label for the y-axis. Defaults to "Longitude".
            zlabel (str, optional): Label for the z-axis. Defaults to "Elevation (m)".
        """
        if not self.profiles:
            print("No profiles to plot.")
            return

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        for name, profile in self.profiles.items():
            ax.plot(
                profile.get_latitudes(),
                profile.get_longitudes(),
                profile.get_elevations(),
                label=name,
                linewidth=1.5,
            )

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)
        ax.legend()
        plt.tight_layout()
        plt.show()


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
                if Point.haversine_distance(gpx1[i],gpx2[j]) < distance:
                    index1 = i
                    index2 = j
                    distance = Point.haversine_distance(gpx1[i],gpx2[j])
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
            if Point.haversine_distance(gpx1[i].di, gpx2[i]) < tolerance:
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
        gpx_points_1 = Track.from_gpx_file(gpx_file_1).points
        gpx_points_2 = Track.from_gpx_file(gpx_file_2).points

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
