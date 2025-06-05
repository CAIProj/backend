import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.interpolate import griddata
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from models import Point, ElevationProfile, Track
from elevation_api import OpenElevationAPI
from typing import Optional, List, Union, Tuple, Dict

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

def plot2d(args):
    gpx_file_1 = args.gpx1
    gpx_file_2 = args.gpx2

    try:
        track_1 = Track.from_gpx_file(gpx_file_1)
        track_2 = Track.from_gpx_file(gpx_file_2)

        # truncate longer file
        min_len = min(len(track_1.points), len(track_2.points))
        track_1.points = track_1.points[:min_len]
        track_2.points = track_2.points[:min_len]

        ElevationPlotter.plot_comparison(track_1.elevation_profile, track_2.elevation_profile)
    except:
        raise

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
