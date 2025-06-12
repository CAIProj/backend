import matplotlib.pyplot as plt
from models import ElevationProfile
from typing import Optional, List, Union, Tuple, Dict

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
