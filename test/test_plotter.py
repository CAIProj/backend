import pytest
from unittest.mock import patch, MagicMock

# Import the Plotter class from your application's plotter.py file.
# Import ElevationProfile and Point from your models.py file, as they are used
# to create dummy data for testing the Plotter.
from plotter import Plotter
from models import ElevationProfile, Point

# Fixture to mock matplotlib.pyplot.
# This ensures that when plotting methods are called in Plotter, they
# interact with mock objects instead of actually rendering plots,
# which would make tests slow and require a display environment.
@pytest.fixture(autouse=True)
def mock_matplotlib():
    """
    Mocks matplotlib.pyplot to prevent actual plot rendering during unit tests.
    It patches the 'plt' object *within* the 'plotter' module, ensuring that
    any calls to 'plt' from 'Plotter' instance methods are intercepted.
    """
    # Use patch context manager to replace 'matplotlib.pyplot' as 'plt' within 'plotter' module.
    # The target string 'plotter.plt' is crucial because that's how it's imported in plotter.py.
    with patch('plotter.plt') as mock_plt:
        # Create a MagicMock object to represent the Figure object returned by plt.figure().
        mock_fig = MagicMock()
        # Create another MagicMock object to represent the Axes object returned by fig.add_subplot().
        mock_ax = MagicMock()

        # Configure the mock 'plt.figure()' call to return our mock_fig.
        mock_plt.figure.return_value = mock_fig
        # Configure the mock_fig's 'add_subplot()' method to return our mock_ax.
        # This simulates the hierarchy: plt.figure() -> fig.add_subplot() -> ax.
        mock_fig.add_subplot.return_value = mock_ax

        # Explicitly mock common matplotlib functions that Plotter calls directly on 'plt'.
        # This makes sure these methods are callable on the mock_plt and their calls can be asserted.
        mock_plt.plot = MagicMock()
        mock_plt.title = MagicMock()
        mock_plt.xlabel = MagicMock()
        mock_plt.ylabel = MagicMock()
        mock_plt.grid = MagicMock()
        mock_plt.legend = MagicMock()
        mock_plt.tight_layout = MagicMock()
        mock_plt.show = MagicMock()

        # Explicitly mock methods that Plotter calls on the Axes object (mock_ax) for 3D plots.
        mock_ax.plot = MagicMock()
        mock_ax.set_title = MagicMock()
        mock_ax.set_xlabel = MagicMock()
        mock_ax.set_ylabel = MagicMock()
        mock_ax.set_zlabel = MagicMock()
        mock_ax.legend = MagicMock()

        # 'yield' makes this a 'yield fixture', meaning the mocked environment
        # is set up before each test and torn down afterward.
        yield mock_plt

# Fixture to create a dummy ElevationProfile instance for tests.
# This provides a consistent and valid ElevationProfile object for various test scenarios.
@pytest.fixture
def dummy_elevation_profile():
    """
    Provides a simple ElevationProfile instance for testing.
    This uses actual Point and ElevationProfile classes from models.py,
    ensuring their methods (like get_distances, get_elevations etc.) are functional
    and return expected values based on the provided points.
    """
    points = [
        Point(latitude=1.0, longitude=1.0, elevation=10.0),
        Point(latitude=2.0, longitude=2.0, elevation=20.0),
        Point(latitude=3.0, longitude=3.0, elevation=15.0),
    ]
    return ElevationProfile(points)

# Fixture to create another dummy ElevationProfile instance, distinct from the first.
@pytest.fixture
def another_dummy_elevation_profile():
    """
    Provides a second, distinct ElevationProfile instance for tests requiring multiple profiles.
    """
    points = [
        Point(latitude=1.5, longitude=1.5, elevation=12.0),
        Point(latitude=2.5, longitude=2.5, elevation=22.0),
        Point(latitude=3.5, longitude=3.5, elevation=17.0),
    ]
    return ElevationProfile(points)


# Test suite for the Plotter class.
class TestPlotter:
    """
    Contains unit tests for the Plotter class in plotter.py.
    """

    # Test cases for the __init__ method.
    def test_init_no_profiles(self):
        """
        Tests Plotter initialization with no profiles provided.
        Asserts that the 'profiles' dictionary is empty.
        """
        plotter = Plotter()
        assert plotter.profiles == {}

    def test_init_with_single_profile_auto_named(self, dummy_elevation_profile):
        """
        Tests Plotter initialization with a single ElevationProfile instance.
        Expects the profile to be auto-named "Profile 1".
        """
        plotter = Plotter([dummy_elevation_profile])
        assert len(plotter.profiles) == 1
        assert "Profile 1" in plotter.profiles
        assert plotter.profiles["Profile 1"] is dummy_elevation_profile

    def test_init_with_single_profile_named(self, dummy_elevation_profile):
        """
        Tests Plotter initialization with a single (ElevationProfile, name) tuple.
        Expects the profile to be named as specified.
        """
        plotter = Plotter([(dummy_elevation_profile, "My Hike")])
        assert len(plotter.profiles) == 1
        assert "My Hike" in plotter.profiles
        assert plotter.profiles["My Hike"] is dummy_elevation_profile

    def test_init_with_single_profile_named_none(self, dummy_elevation_profile):
        """
        Tests Plotter initialization when a profile is provided with a None name.
        Expects the profile to be auto-named (e.g., "Profile 1").
        """
        plotter = Plotter([(dummy_elevation_profile, None)])
        assert len(plotter.profiles) == 1
        assert "Profile 1" in plotter.profiles
        assert plotter.profiles["Profile 1"] is dummy_elevation_profile

    def test_init_with_multiple_profiles_auto_named(self, dummy_elevation_profile, another_dummy_elevation_profile):
        """
        Tests Plotter initialization with multiple ElevationProfile instances,
        all of which should be auto-named sequentially.
        """
        plotter = Plotter([dummy_elevation_profile, another_dummy_elevation_profile])
        assert len(plotter.profiles) == 2
        assert "Profile 1" in plotter.profiles
        assert "Profile 2" in plotter.profiles

    def test_init_with_multiple_profiles_mixed_names(self, dummy_elevation_profile, another_dummy_elevation_profile):
        """
        Tests Plotter initialization with a mix of auto-named and explicitly named profiles.
        """
        plotter = Plotter([dummy_elevation_profile, (another_dummy_elevation_profile, "Named Profile")])
        assert len(plotter.profiles) == 2
        assert "Profile 1" in plotter.profiles
        assert "Named Profile" in plotter.profiles

    # Test cases for the _generate_unique_name method.
    def test_generate_unique_name_empty(self):
        """
        Tests _generate_unique_name when no profiles exist.
        Should return "Profile 1".
        """
        plotter = Plotter()
        assert plotter._generate_unique_name() == "Profile 1"

    def test_generate_unique_name_existing(self, dummy_elevation_profile):
        """
        Tests _generate_unique_name when "Profile 1" already exists.
        Should return "Profile 2".
        """
        plotter = Plotter()
        plotter.add_profiles((dummy_elevation_profile, "Profile 1"))
        assert plotter._generate_unique_name() == "Profile 2"

    def test_generate_unique_name_with_gap(self, dummy_elevation_profile):
        """
        Tests _generate_unique_name when a gap exists in profile numbering.
        Should find the first available sequential number.
        """
        plotter = Plotter()
        plotter.add_profiles((dummy_elevation_profile, "Profile 1"))
        plotter.add_profiles((dummy_elevation_profile, "Profile 3")) # Add Profile 3
        assert plotter._generate_unique_name() == "Profile 2" # Should find the gap

    # Test cases for the add_profiles method.
    def test_add_profiles_single_auto_name(self, dummy_elevation_profile):
        """
        Tests adding a single ElevationProfile without a name, expecting auto-naming.
        """
        plotter = Plotter()
        plotter.add_profiles(dummy_elevation_profile)
        assert "Profile 1" in plotter.profiles
        assert plotter.profiles["Profile 1"] is dummy_elevation_profile

    def test_add_profiles_single_named(self, dummy_elevation_profile):
        """
        Tests adding a single ElevationProfile with an explicit name.
        """
        plotter = Plotter()
        plotter.add_profiles((dummy_elevation_profile, "My Unique Name"))
        assert "My Unique Name" in plotter.profiles
        assert plotter.profiles["My Unique Name"] is dummy_elevation_profile

    def test_add_profiles_multiple_named(self, dummy_elevation_profile, another_dummy_elevation_profile):
        """
        Tests adding multiple ElevationProfiles with explicit names.
        """
        plotter = Plotter()
        plotter.add_profiles((dummy_elevation_profile, "Track A"), (another_dummy_elevation_profile, "Track B"))
        assert "Track A" in plotter.profiles
        assert "Track B" in plotter.profiles
        assert plotter.profiles["Track A"] is dummy_elevation_profile
        assert plotter.profiles["Track B"] is another_dummy_elevation_profile

    def test_add_profiles_mixed_input(self, dummy_elevation_profile, another_dummy_elevation_profile):
        """
        Tests adding a mix of auto-named and explicitly named profiles.
        """
        plotter = Plotter()
        plotter.add_profiles(dummy_elevation_profile, (another_dummy_elevation_profile, "Specific Track"))
        assert "Profile 1" in plotter.profiles
        assert "Specific Track" in plotter.profiles

    def test_add_profiles_duplicate_name_overwrites(self, dummy_elevation_profile, another_dummy_elevation_profile):
        """
        Tests that adding a profile with an existing name overwrites the old one.
        """
        plotter = Plotter()
        plotter.add_profiles((dummy_elevation_profile, "Common Name"))
        # Add another profile with the same name, expecting overwrite
        plotter.add_profiles((another_dummy_elevation_profile, "Common Name"))
        assert "Common Name" in plotter.profiles
        # Assert that the profile under "Common Name" is now 'another_dummy_elevation_profile'
        assert plotter.profiles["Common Name"] is another_dummy_elevation_profile
        assert len(plotter.profiles) == 1 # Should still be only one entry with that name

    def test_add_profiles_empty_string_name_auto_named(self, dummy_elevation_profile):
        """
        Tests adding a profile with an empty string as a name, expecting auto-naming.
        """
        plotter = Plotter()
        plotter.add_profiles((dummy_elevation_profile, ""))
        assert "Profile 1" in plotter.profiles
        assert len(plotter.profiles) == 1

    def test_add_profiles_none_name_auto_named(self, dummy_elevation_profile):
        """
        Tests adding a profile with None as a name, expecting auto-naming.
        """
        plotter = Plotter()
        plotter.add_profiles((dummy_elevation_profile, None))
        assert "Profile 1" in plotter.profiles
        assert len(plotter.profiles) == 1

    def test_add_profiles_invalid_input(self):
        """
        Tests add_profiles with various invalid input types, asserting ValueError is raised.
        The match string uses 'r"\\("', 'r"\\)"' to escape parentheses for regex.
        """
        plotter = Plotter()
        # Test with a string that is not an ElevationProfile
        with pytest.raises(ValueError, match=r"Provide either ElevationProfile or \(ElevationProfile, name\) tuples."):
            plotter.add_profiles("invalid_string")
        # Test with a tuple where the first element is not an ElevationProfile
        with pytest.raises(ValueError, match=r"Provide either ElevationProfile or \(ElevationProfile, name\) tuples."):
            plotter.add_profiles((123, "name"))
        # Test with a tuple where the first element is a MagicMock (not an actual ElevationProfile)
        with pytest.raises(ValueError, match=r"Provide either ElevationProfile or \(ElevationProfile, name\) tuples."):
            plotter.add_profiles((MagicMock(), "name"))

    # Test cases for the set_profiles method.
    def test_set_profiles_valid(self, dummy_elevation_profile, another_dummy_elevation_profile):
        """
        Tests set_profiles with a valid dictionary of profiles.
        Asserts that the plotter's profiles dictionary is correctly replaced.
        """
        plotter = Plotter()
        new_profiles = {"New Track 1": dummy_elevation_profile, "New Track 2": another_dummy_elevation_profile}
        plotter.set_profiles(new_profiles)
        assert plotter.profiles == new_profiles

    def test_set_profiles_empty_dict(self, dummy_elevation_profile):
        """
        Tests set_profiles with an empty dictionary.
        Ensures existing profiles are cleared.
        """
        plotter = Plotter([dummy_elevation_profile]) # Start with a valid profile
        plotter.set_profiles({})
        assert plotter.profiles == {}

    def test_set_profiles_invalid_type(self):
        """
        Tests set_profiles with a non-dictionary input, asserting TypeError.
        """
        plotter = Plotter()
        with pytest.raises(TypeError, match="Profiles must be provided as a dictionary"):
            plotter.set_profiles([("name", MagicMock())])

    def test_set_profiles_invalid_value(self):
        """
        Tests set_profiles with a dictionary containing non-ElevationProfile values,
        asserting ValueError.
        """
        plotter = Plotter()
        with pytest.raises(ValueError, match="Invalid profile for 'bad_profile': must be an ElevationProfile."):
            plotter.set_profiles({"bad_profile": "not an ElevationProfile"})
        with pytest.raises(ValueError, match="Invalid profile for 'another_bad': must be an ElevationProfile."):
            plotter.set_profiles({"another_bad": MagicMock()}) # MagicMock is not an ElevationProfile instance


    # Test cases for plotting methods (focus on mocking matplotlib calls).
    def test_plot_distance_vs_elevation_no_profiles(self, capsys, mock_matplotlib):
        """
        Tests plot_distance_vs_elevation when no profiles are loaded.
        Asserts that a message is printed and no plotting functions are called.
        """
        plotter = Plotter()
        plotter.plot_distance_vs_elevation()
        captured = capsys.readouterr() # Captures stdout/stderr
        assert "No profiles to plot." in captured.out
        # Assert that no matplotlib plotting functions were called
        mock_matplotlib.plot.assert_not_called()
        mock_matplotlib.show.assert_not_called()
        mock_matplotlib.figure.assert_not_called()

    def test_plot_distance_vs_elevation_single_profile(self, dummy_elevation_profile, mock_matplotlib):
        """
        Tests plot_distance_vs_elevation with a single profile.
        Asserts that matplotlib functions are called with expected arguments.
        """
        plotter = Plotter([dummy_elevation_profile])
        plotter.plot_distance_vs_elevation(title="My Plot", xlabel="Dist", ylabel="Elev")

        # Assert plt.figure was called exactly once with the specified figsize.
        mock_matplotlib.figure.assert_called_once_with(figsize=(12, 6))
        # Assert plt.plot was called exactly once with the profile's data and label.
        mock_matplotlib.plot.assert_called_once_with(
            dummy_elevation_profile.get_distances(),
            dummy_elevation_profile.get_elevations(),
            label="Profile 1",
            linewidth=2
        )
        # Assert other matplotlib methods were called with the correct titles/labels.
        mock_matplotlib.title.assert_called_once_with("My Plot")
        mock_matplotlib.xlabel.assert_called_once_with("Dist")
        mock_matplotlib.ylabel.assert_called_once_with("Elev")
        mock_matplotlib.grid.assert_called_once_with(True, alpha=0.3)
        mock_matplotlib.legend.assert_called_once()
        mock_matplotlib.tight_layout.assert_called_once()
        mock_matplotlib.show.assert_called_once()

    def test_plot_distance_vs_elevation_multiple_profiles(self, dummy_elevation_profile, another_dummy_elevation_profile, mock_matplotlib):
        """
        Tests plot_distance_vs_elevation with multiple profiles.
        Asserts that plt.plot is called for each profile.
        """
        plotter = Plotter([dummy_elevation_profile, another_dummy_elevation_profile])
        plotter.plot_distance_vs_elevation()

        # Assert plt.figure was called once for the plot.
        mock_matplotlib.figure.assert_called_once_with(figsize=(12, 6))
        # Assert plt.plot was called twice (once for each profile).
        assert mock_matplotlib.plot.call_count == 2

        # Define the expected calls for plt.plot.
        # This checks the positional and keyword arguments passed to plot().
        expected_calls = [
            ((dummy_elevation_profile.get_distances(), dummy_elevation_profile.get_elevations()), {'label': 'Profile 1', 'linewidth': 2}),
            ((another_dummy_elevation_profile.get_distances(), another_dummy_elevation_profile.get_elevations()), {'label': 'Profile 2', 'linewidth': 2}),
        ]

        # Verify that the actual calls match the expected calls.
        assert len(mock_matplotlib.plot.call_args_list) == len(expected_calls)
        for i, call_args in enumerate(mock_matplotlib.plot.call_args_list):
            args, kwargs = call_args
            assert args == expected_calls[i][0]
            assert kwargs == expected_calls[i][1]

        # Assert other matplotlib methods were called once.
        mock_matplotlib.title.assert_called_once()
        mock_matplotlib.xlabel.assert_called_once()
        mock_matplotlib.ylabel.assert_called_once()
        mock_matplotlib.grid.assert_called_once()
        mock_matplotlib.legend.assert_called_once()
        mock_matplotlib.tight_layout.assert_called_once()
        mock_matplotlib.show.assert_called_once()


    def test_plot_3d_lat_lon_elevation_no_profiles(self, capsys, mock_matplotlib):
        """
        Tests plot_3d_lat_lon_elevation when no profiles are loaded.
        Asserts that a message is printed and no plotting functions are called.
        """
        plotter = Plotter()
        plotter.plot_3d_lat_lon_elevation()
        captured = capsys.readouterr()
        assert "No profiles to plot." in captured.out
        # Assert that the add_subplot method on the figure mock was not called.
        mock_matplotlib.figure.return_value.add_subplot.assert_not_called()
        mock_matplotlib.show.assert_not_called()
        mock_matplotlib.figure.assert_not_called()

    def test_plot_3d_lat_lon_elevation_single_profile(self, dummy_elevation_profile, mock_matplotlib):
        """
        Tests plot_3d_lat_lon_elevation with a single profile.
        Asserts correct calls to matplotlib's 3D plotting functions.
        """
        plotter = Plotter([dummy_elevation_profile])
        plotter.plot_3d_lat_lon_elevation(title="3D View", xlabel="Lat", ylabel="Lon", zlabel="Z")

        # Get the mock objects that represent the Figure and Axes for easier assertion.
        mock_fig = mock_matplotlib.figure.return_value
        mock_ax = mock_fig.add_subplot.return_value

        # Assert plt.figure was called once to create the figure.
        mock_matplotlib.figure.assert_called_once()
        # Assert add_subplot was called on the figure to create a 3D subplot.
        mock_fig.add_subplot.assert_called_once_with(111, projection="3d")
        # Assert ax.plot was called for the profile with latitude, longitude, and elevation.
        mock_ax.plot.assert_called_once_with(
            dummy_elevation_profile.get_latitudes(),
            dummy_elevation_profile.get_longitudes(),
            dummy_elevation_profile.get_elevations(),
            label="Profile 1",
            linewidth=1.5
        )
        # Assert axis labels and title are set correctly.
        mock_ax.set_title.assert_called_once_with("3D View")
        mock_ax.set_xlabel.assert_called_once_with("Lat")
        mock_ax.set_ylabel.assert_called_once_with("Lon")
        mock_ax.set_zlabel.assert_called_once_with("Z")
        mock_ax.legend.assert_called_once()
        mock_matplotlib.tight_layout.assert_called_once()
        mock_matplotlib.show.assert_called_once()

    def test_plot_3d_lat_lon_elevation_multiple_profiles(self, dummy_elevation_profile, another_dummy_elevation_profile, mock_matplotlib):
        """
        Tests plot_3d_lat_lon_elevation with multiple profiles.
        Asserts ax.plot is called for each profile.
        """
        plotter = Plotter([dummy_elevation_profile, another_dummy_elevation_profile])
        plotter.plot_3d_lat_lon_elevation()

        mock_fig = mock_matplotlib.figure.return_value
        mock_ax = mock_fig.add_subplot.return_value

        mock_matplotlib.figure.assert_called_once()
        mock_fig.add_subplot.assert_called_once_with(111, projection="3d")
        assert mock_ax.plot.call_count == 2 # Expect two calls to ax.plot

        # Define the expected calls for ax.plot, including positional and keyword arguments.
        expected_calls = [
            ((dummy_elevation_profile.get_latitudes(), dummy_elevation_profile.get_longitudes(), dummy_elevation_profile.get_elevations()), {'label': 'Profile 1', 'linewidth': 1.5}),
            ((another_dummy_elevation_profile.get_latitudes(), another_dummy_elevation_profile.get_longitudes(), another_dummy_elevation_profile.get_elevations()), {'label': 'Profile 2', 'linewidth': 1.5}),
        ]

        # Verify that the actual calls match the expected calls.
        assert len(mock_ax.plot.call_args_list) == len(expected_calls)
        for i, call_args in enumerate(mock_ax.plot.call_args_list):
            args, kwargs = call_args
            assert args == expected_calls[i][0]
            assert kwargs == expected_calls[i][1]

        mock_ax.set_title.assert_called_once()
        mock_ax.set_xlabel.assert_called_once()
        mock_ax.set_ylabel.assert_called_once()
        mock_ax.set_zlabel.assert_called_once()
        mock_ax.legend.assert_called_once()
        mock_matplotlib.tight_layout.assert_called_once()
        mock_matplotlib.show.assert_called_once()