import unittest
from unittest.mock import patch, Mock
import requests  # Required to mock requests.ConnectionError
import json      # Used for handling JSON in mock responses
import sys       # Used for patching sys.stdout
from io import StringIO # Used to capture stdout output

# Import the classes from your project that we are testing or depend on
from models import Point
from elevation_api import ElevationAPI, OpenElevationAPI

class TestElevationAPI(unittest.TestCase):
    """
    Test suite for the ElevationAPI class in elevation_api.py.
    These tests focus on the behavior of get_elevations under various conditions,
    mocking external API calls using the 'requests' library.
    """

    def setUp(self):
        """
        Set up common mock data for tests. This method runs before each test method.
        """
        # Create some dummy Point objects to use as input for get_elevations
        self.mock_point1 = Point(latitude=40.7128, longitude=-74.0060, elevation=None)
        self.mock_point2 = Point(latitude=34.0522, longitude=-118.2437, elevation=None)
        self.mock_points = [self.mock_point1, self.mock_point2]

    @patch('elevation_api.requests.post')
    def test_get_elevations_empty_list(self, mock_post):
        """
        Test get_elevations() with an empty list of points.
        It should return an empty list and ensure no actual API call is made.
        """
        # Call the method under test with an empty list
        result = ElevationAPI.get_elevations([])

        # Assertions
        # 1. Verify that an empty list is returned.
        self.assertEqual(result, [])
        # 2. Verify that requests.post was never called, as there are no points to send.
        mock_post.assert_not_called()

    @patch('elevation_api.requests.post')
    def test_get_elevations_success(self, mock_post):
        """
        Test get_elevations() with a successful API response from ElevationAPI.
        This verifies that the elevations are correctly extracted from the mock response.
        """
        # 1. Create a mock response object that simulates a successful HTTP response.
        mock_response = Mock()
        mock_response.ok = True # Simulate a 2xx status code (e.g., 200 OK)

        # 2. Define the content of the mock response.
        #    ElevationAPI expects 'height' in its JSON response.
        #    We convert a Python dict to JSON string, then to bytes.
        mock_response.content = json.dumps({"height": [10.5, 20.1]}).encode('utf-8')
        
        # 3. Configure the patched requests.post to return our mock_response.
        mock_post.return_value = mock_response

        # Call the method under test with our mock points
        result = ElevationAPI.get_elevations(self.mock_points)

        # Assertions
        # 1. Define the expected elevations based on our mock response content.
        expected_elevations = [10.5, 20.1]
        # 2. Verify that the method returned the correct elevations.
        self.assertEqual(result, expected_elevations)
        # 3. Verify that requests.post was called exactly once with the correct URL
        #    and the correctly formatted JSON payload for ElevationAPI.
        mock_post.assert_called_once_with(
            ElevationAPI.API_URL,
            json={"shape": [{"lat": 40.7128, "lon": -74.0060}, {"lat": 34.0522, "lon": -118.2437}]}
        )

    @patch('elevation_api.requests.post')
    @patch('sys.stdout', new_callable=StringIO) # Patch sys.stdout to capture printed output
    def test_get_elevations_unsuccessful_api_response(self, mock_stdout, mock_post):
        """
        Test get_elevations() with an unsuccessful API response (e.g., 404, 500 status code).
        It should return an empty list and print an appropriate error message to stdout.
        """
        # 1. Configure the mock response to simulate an unsuccessful HTTP status.
        mock_response = Mock()
        mock_response.ok = False  # Indicate an error status (e.g., 4xx or 5xx)
        mock_response.status_code = 404 # Set a specific example status code
        
        # 2. Configure the patched requests.post to return this unsuccessful mock_response.
        mock_post.return_value = mock_response

        # Call the method under test
        result = ElevationAPI.get_elevations(self.mock_points)

        # Assertions
        # 1. Verify that an empty list is returned, as data retrieval failed.
        self.assertEqual(result, [])
        # 2. Verify that requests.post was called exactly once.
        mock_post.assert_called_once()

        # 3. Verify the content of the printed output (error message).
        #    mock_stdout.getvalue() retrieves the string written to stdout.
        expected_output = "API request failed: Data could not be retrieved\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('elevation_api.requests.post')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_elevations_connection_error(self, mock_stdout, mock_post):
        """
        Test get_elevations() when a requests.ConnectionError occurs (e.g., no internet).
        It should return an empty list and print a connection error message.
        """
        # 1. Configure the patched requests.post to raise a ConnectionError
        #    when it is called.
        mock_post.side_effect = requests.ConnectionError("Test Connection Error")

        # Call the method under test
        result = ElevationAPI.get_elevations(self.mock_points)

        # Assertions
        # 1. Verify that an empty list is returned due to the connection error.
        self.assertEqual(result, [])
        # 2. Verify that requests.post was attempted once before the error.
        mock_post.assert_called_once()

        # 3. Verify the content of the printed connection error message.
        expected_output = "Connection error: Data could not be retrieved\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('elevation_api.requests.post')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_elevations_unexpected_exception(self, mock_stdout, mock_post):
        """
        Test get_elevations() when an unexpected generic Exception occurs during the
        API call or subsequent response processing (e.g., JSON parsing error if not caught).
        It should return an empty list and print a generic unexpected error message.
        """
        # 1. Configure the patched requests.post to raise a generic Exception.
        mock_post.side_effect = Exception("Something unexpected happened")

        # Call the method under test
        result = ElevationAPI.get_elevations(self.mock_points)

        # Assertions
        # 1. Verify that an empty list is returned due to the unexpected error.
        self.assertEqual(result, [])
        # 2. Verify that requests.post was attempted once.
        mock_post.assert_called_once()

        # 3. Verify the content of the printed unexpected error message.
        expected_output = "Unexpected error: Something unexpected happened\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)


class TestOpenElevationAPI(unittest.TestCase):
    """
    Test suite for the OpenElevationAPI class in elevation_api.py.
    These tests mirror those for ElevationAPI but account for the
    OpenElevation API's specific URL and JSON response/request formats.
    """

    def setUp(self):
        """
        Set up common mock data for tests for OpenElevationAPI.
        """
        self.mock_point1 = Point(latitude=40.7128, longitude=-74.0060, elevation=None)
        self.mock_point2 = Point(latitude=34.0522, longitude=-118.2437, elevation=None)
        self.mock_points = [self.mock_point1, self.mock_point2]

    @patch('elevation_api.requests.post')
    def test_get_elevations_empty_list(self, mock_post):
        """
        Test get_elevations() with an empty list of points for OpenElevationAPI.
        It should return an empty list and not make any API calls.
        """
        result = OpenElevationAPI.get_elevations([])
        self.assertEqual(result, [])
        mock_post.assert_not_called()

    @patch('elevation_api.requests.post')
    def test_get_elevations_success(self, mock_post):
        """
        Test get_elevations() with a successful API response for OpenElevationAPI.
        Verifies correct extraction of elevations from OpenElevation's specific JSON format.
        """
        mock_response = Mock()
        mock_response.ok = True
        # OpenElevationAPI expects 'results' which is a list of dicts, each with 'elevation'.
        mock_response.content = json.dumps(
            {"results": [{"latitude": 40.7128, "longitude": -74.0060, "elevation": 10.5},
                         {"latitude": 34.0522, "longitude": -118.2437, "elevation": 20.1}]}
        ).encode('utf-8')
        mock_post.return_value = mock_response

        result = OpenElevationAPI.get_elevations(self.mock_points)

        expected_elevations = [10.5, 20.1]
        self.assertEqual(result, expected_elevations)
        # Verify call with OpenElevationAPI's specific URL and 'locations' payload format.
        mock_post.assert_called_once_with(
            OpenElevationAPI.API_URL,
            json={"locations": [{"latitude": 40.7128, "longitude": -74.0060},
                                {"latitude": 34.0522, "longitude": -118.2437}]}
        )

    @patch('elevation_api.requests.post')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_elevations_unsuccessful_api_response(self, mock_stdout, mock_post):
        """
        Test get_elevations() with an unsuccessful API response for OpenElevationAPI.
        Verifies empty list return and correct error message specific to OpenElevation.
        """
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500 # Example status code for internal server error
        mock_post.return_value = mock_response

        result = OpenElevationAPI.get_elevations(self.mock_points)

        self.assertEqual(result, [])
        mock_post.assert_called_once()

        # Check for the error message specific to OpenElevationAPI.
        expected_output = "API request failed: open-elevation data could not be retrieved\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('elevation_api.requests.post')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_elevations_connection_error(self, mock_stdout, mock_post):
        """
        Test get_elevations() when a requests.ConnectionError occurs for OpenElevationAPI.
        Verifies empty list return and correct connection error message specific to OpenElevation.
        """
        mock_post.side_effect = requests.ConnectionError("Test OpenElevation Connection Error")

        result = OpenElevationAPI.get_elevations(self.mock_points)

        self.assertEqual(result, [])
        mock_post.assert_called_once()

        # Check for the connection error message specific to OpenElevationAPI.
        expected_output = "Connection error: open-elevation data could not be retrieved\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('elevation_api.requests.post')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_elevations_unexpected_exception(self, mock_stdout, mock_post):
        """
        Test get_elevations() when an unexpected Exception occurs for OpenElevationAPI.
        Verifies empty list return and correct generic error message specific to OpenElevation.
        """
        mock_post.side_effect = Exception("OpenElevation unexpected error")

        result = OpenElevationAPI.get_elevations(self.mock_points)

        self.assertEqual(result, [])
        mock_post.assert_called_once()

        # Check for the unexpected error message specific to OpenElevationAPI.
        expected_output = "Unexpected error: OpenElevation unexpected error\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)


if __name__ == '__main__':
    unittest.main()