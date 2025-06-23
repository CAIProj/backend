"""
Unit tests for GPX Track interpolation and alignment functionality.

This module tests the GPX Track methods for interpolating tracks to matching
point counts and aligning tracks by their endpoints.

Run with: python -m unittest test.test_gpx_functionality
"""

import unittest
import sys
import os
import math

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock external dependencies for testing environments without full setup
class MockGeoidKarney:
    def __init__(self, file):
        pass
    def __call__(self, location):
        return 0.0

class MockLatLon:
    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon

class MockGpxpy:
    pass

# Monkey patch imports for testing without dependencies
sys.modules['pygeodesy'] = type('module', (), {'GeoidKarney': MockGeoidKarney})()
sys.modules['pygeodesy.ellipsoidalKarney'] = type('module', (), {'LatLon': MockLatLon})()
sys.modules['gpxpy'] = MockGpxpy()

# Import our models
from gpx_dataengine.models import Track, Point


class TestGPXInterpolation(unittest.TestCase):
    """Test cases for GPX Track interpolation functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Full route with 5 points
        self.full_route_points = [
            (47.3769, 8.5417, 408.0),
            (47.3770, 8.5420, 410.0),
            (47.3772, 8.5425, 415.0),
            (47.3775, 8.5430, 420.0),
            (47.3780, 8.5440, 430.0)
        ]
        
        # Subset route with 3 points
        self.subset_route_points = [
            (47.3769, 8.5417, 408.0),
            (47.3775, 8.5430, 420.0),
            (47.3780, 8.5440, 430.0)
        ]
        
        self.full_route = self._create_test_track(self.full_route_points)
        self.subset_route = self._create_test_track(self.subset_route_points)
    
    def _create_test_track(self, points_data):
        """Helper method to create a Track from list of (lat, lon, elev) tuples."""
        points = [Point(lat, lon, elev) for lat, lon, elev in points_data]
        return Track(points)
    
    def test_interpolation_basic(self):
        """Test basic interpolation functionality."""
        interpolated = Track.interpolate_to_match_points(self.full_route, self.subset_route)
        
        # Verify point count matches target
        self.assertEqual(len(interpolated.points), len(self.subset_route.points))
        
        # Verify start and end points are preserved
        self.assertAlmostEqual(interpolated.points[0].latitude, 
                              self.full_route.points[0].latitude, places=6)
        self.assertAlmostEqual(interpolated.points[-1].latitude, 
                              self.full_route.points[-1].latitude, places=6)
    
    def test_interpolation_upsampling(self):
        """Test interpolation when increasing point count."""
        # Create smaller reference track
        small_points = [
            (47.3769, 8.5417, 408.0),
            (47.3775, 8.5430, 420.0),
            (47.3780, 8.5440, 430.0)
        ]
        small_track = self._create_test_track(small_points)
        
        # Create target with more points
        large_points = [(47.3769, 8.5417, 408.0)] * 6
        large_track = self._create_test_track(large_points)
        
        interpolated = Track.interpolate_to_match_points(small_track, large_track)
        
        self.assertEqual(len(interpolated.points), 6)
        self.assertGreater(len(interpolated.points), len(small_track.points))
    
    def test_interpolation_error_conditions(self):
        """Test error handling for invalid inputs."""
        single_point = self._create_test_track([(47.0, 8.0, 400.0)])
        
        with self.assertRaises(ValueError):
            Track.interpolate_to_match_points(single_point, self.subset_route)
        
        with self.assertRaises(ValueError):
            Track.interpolate_to_match_points(self.full_route, single_point)


class TestGPXAlignment(unittest.TestCase):
    """Test cases for GPX Track alignment functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.track1_points = [
            (47.3769, 8.5417, 408.0),
            (47.3770, 8.5420, 410.0),
            (47.3772, 8.5425, 415.0),
            (47.3775, 8.5430, 420.0),
            (47.3780, 8.5440, 430.0)
        ]
        
        self.track2_points = [
            (47.3769, 8.5417, 408.0),
            (47.3771, 8.5422, 412.0),
            (47.3774, 8.5428, 418.0),
            (47.3780, 8.5440, 430.0)
        ]
        
        self.track1 = self._create_test_track(self.track1_points)
        self.track2 = self._create_test_track(self.track2_points)
    
    def _create_test_track(self, points_data):
        """Helper method to create a Track from list of (lat, lon, elev) tuples."""
        points = [Point(lat, lon, elev) for lat, lon, elev in points_data]
        return Track(points)
    
    def test_alignment_basic(self):
        """Test basic alignment functionality."""
        aligned1, aligned2 = Track.align_track_endpoints(self.track1, self.track2)
        
        # Verify tracks are returned
        self.assertIsNotNone(aligned1)
        self.assertIsNotNone(aligned2)
        self.assertGreater(len(aligned1.points), 0)
        self.assertGreater(len(aligned2.points), 0)
        
        # Verify alignment within tolerance
        start_distance = aligned1.points[0].distance_to(aligned2.points[0])
        end_distance = aligned1.points[-1].distance_to(aligned2.points[-1])
        
        self.assertLess(start_distance, 0.1)
        self.assertLess(end_distance, 0.1)
    
    def test_alignment_tolerance(self):
        """Test alignment with different tolerance settings."""
        # Create tracks with points ~100m apart
        track1_points = [
            (47.3769, 8.5417, 408.0),
            (47.3780, 8.5440, 430.0)
        ]
        
        track2_points = [
            (47.3770, 8.5418, 410.0),  # ~100m from first track
            (47.3781, 8.5441, 432.0)
        ]
        
        track1 = self._create_test_track(track1_points)
        track2 = self._create_test_track(track2_points)
        
        # Should work with loose tolerance
        aligned1, aligned2 = Track.align_track_endpoints(track1, track2, tolerance_km=0.2)
        self.assertIsNotNone(aligned1)
        self.assertIsNotNone(aligned2)
    
    def test_alignment_error_conditions(self):
        """Test error handling for alignment."""
        single_point = self._create_test_track([(47.0, 8.0, 400.0)])
        
        with self.assertRaises(ValueError):
            Track.align_track_endpoints(single_point, self.track2)
        
        # Test tracks too far apart
        far_track_points = [
            (40.7128, -74.0060, 100.0),  # New York coordinates
            (40.7130, -74.0058, 110.0)
        ]
        far_track = self._create_test_track(far_track_points)
        
        with self.assertRaises(ValueError):
            Track.align_track_endpoints(self.track1, far_track, tolerance_km=0.1)


class TestDistanceCalculation(unittest.TestCase):
    """Test cases for distance calculation methods."""
    
    def test_point_distance(self):
        """Test Point distance calculation."""
        p1 = Point(47.3769, 8.5417, 408.0)
        p2 = Point(47.3780, 8.5440, 430.0)
        
        distance = p1.distance_to(p2)
        
        # Should be positive and reasonable for Zurich coordinates
        self.assertGreater(distance, 0)
        self.assertLess(distance, 1.0)  # Less than 1km
    
    def test_track_total_distance(self):
        """Test Track total distance calculation."""
        points = [
            Point(47.3769, 8.5417, 408.0),
            Point(47.3770, 8.5420, 410.0),
            Point(47.3772, 8.5425, 415.0)
        ]
        track = Track(points)
        
        total_distance = track.total_distance
        self.assertGreater(total_distance, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)