"""
Unit tests for GPX Track interpolation functionality using unittest framework.

This module contains proper unit tests that can be run with standard Python test runners.
Run with: python -m unittest test.test_gpx_interpolation_unittest
Or: python -m pytest test/test_gpx_interpolation_unittest.py
"""

import unittest
import sys
import os
import tempfile
import math

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock external dependencies for testing
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

# Monkey patch the imports before importing our modules
sys.modules['pygeodesy'] = type('module', (), {'GeoidKarney': MockGeoidKarney})()
sys.modules['pygeodesy.ellipsoidalKarney'] = type('module', (), {'LatLon': MockLatLon})()
sys.modules['gpxpy'] = MockGpxpy()

# Now import our models
from gpx_dataengine.models import Track, Point


class TestGPXInterpolation(unittest.TestCase):
    """Test cases for GPX Track interpolation functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create standard test tracks for reuse
        self.reference_track_points = [
            (0.000, 0.000, 100.0),
            (0.001, 0.001, 110.0),
            (0.002, 0.002, 120.0),
            (0.003, 0.003, 130.0),
            (0.004, 0.004, 140.0)
        ]
        
        self.target_track_points = [
            (0.000, 0.000, 200.0),
            (0.002, 0.002, 220.0),
            (0.004, 0.004, 240.0)
        ]
        
        self.reference_track = self._create_test_track(self.reference_track_points)
        self.target_track = self._create_test_track(self.target_track_points)
    
    def _create_test_track(self, points_data):
        """Helper method to create a Track from list of (lat, lon, elev) tuples."""
        points = [Point(lat, lon, elev) for lat, lon, elev in points_data]
        return Track(points)
    
    def test_basic_interpolation(self):
        """Test basic interpolation functionality."""
        # Interpolate reference track to match target track point count
        interpolated = Track.interpolate_to_match_points(self.reference_track, self.target_track)
        
        # Verify point count matches target
        self.assertEqual(len(interpolated.points), len(self.target_track.points))
        
        # Verify start and end points are preserved
        self.assertAlmostEqual(interpolated.points[0].latitude, self.reference_track.points[0].latitude, places=6)
        self.assertAlmostEqual(interpolated.points[0].longitude, self.reference_track.points[0].longitude, places=6)
        self.assertAlmostEqual(interpolated.points[-1].latitude, self.reference_track.points[-1].latitude, places=6)
        self.assertAlmostEqual(interpolated.points[-1].longitude, self.reference_track.points[-1].longitude, places=6)
    
    def test_upsampling(self):
        """Test interpolation when increasing point count (upsampling)."""
        # Create a smaller reference track
        small_reference_points = [
            (0.000, 0.000, 100.0),
            (0.002, 0.002, 120.0),
            (0.004, 0.004, 140.0)
        ]
        small_reference = self._create_test_track(small_reference_points)
        
        # Create target with more points
        large_target_points = [(0.0, 0.0, 0.0)] * 6
        large_target = self._create_test_track(large_target_points)
        
        # Interpolate
        interpolated = Track.interpolate_to_match_points(small_reference, large_target)
        
        # Verify upsampling
        self.assertEqual(len(interpolated.points), 6)
        self.assertGreater(len(interpolated.points), len(small_reference.points))
        
        # Verify interpolated points lie on expected path
        for point in interpolated.points:
            # For linear track, lat should approximately equal lon
            self.assertAlmostEqual(point.latitude, point.longitude, delta=0.0001)
            # Elevation should be between start and end values
            self.assertGreaterEqual(point.elevation, 100.0)
            self.assertLessEqual(point.elevation, 140.0)
    
    def test_downsampling(self):
        """Test interpolation when decreasing point count (downsampling)."""
        # Use the longer reference track and shorter target
        interpolated = Track.interpolate_to_match_points(self.reference_track, self.target_track)
        
        # Verify downsampling
        self.assertEqual(len(interpolated.points), 3)
        self.assertLess(len(interpolated.points), len(self.reference_track.points))
        
        # Verify key points are preserved
        self.assertAlmostEqual(interpolated.points[0].elevation, 100.0, delta=0.1)
        self.assertAlmostEqual(interpolated.points[-1].elevation, 140.0, delta=0.1)
    
    def test_none_elevations(self):
        """Test interpolation with None elevation values."""
        # Create track with None elevations
        none_elevation_points = [
            (0.000, 0.000, None),
            (0.001, 0.001, None),
            (0.002, 0.002, None)
        ]
        none_track = self._create_test_track(none_elevation_points)
        
        # Create target track
        target_points = [(0.0, 0.0, 0.0), (0.001, 0.001, 0.0)]
        target = self._create_test_track(target_points)
        
        # Interpolate
        interpolated = Track.interpolate_to_match_points(none_track, target)
        
        # Verify None elevations are preserved
        for point in interpolated.points:
            self.assertIsNone(point.elevation)
    
    def test_mixed_elevations(self):
        """Test interpolation with mixed None and numeric elevations."""
        # Create track with mixed elevations
        mixed_elevation_points = [
            (0.000, 0.000, 100.0),
            (0.001, 0.001, None),
            (0.002, 0.002, 120.0)
        ]
        mixed_track = self._create_test_track(mixed_elevation_points)
        
        # Create target track
        target_points = [(0.0, 0.0, 0.0), (0.002, 0.002, 0.0)]
        target = self._create_test_track(target_points)
        
        # Interpolate
        interpolated = Track.interpolate_to_match_points(mixed_track, target)
        
        # Verify elevations are numeric (None values were replaced with 0 for interpolation)
        for point in interpolated.points:
            self.assertIsNotNone(point.elevation)
            self.assertIsInstance(point.elevation, (int, float))
    
    def test_minimum_points(self):
        """Test interpolation with minimum number of points (2 each)."""
        # Create minimal tracks
        min_reference_points = [(0.000, 0.000, 100.0), (0.001, 0.001, 110.0)]
        min_target_points = [(0.0, 0.0, 0.0), (0.001, 0.001, 0.0)]
        
        min_reference = self._create_test_track(min_reference_points)
        min_target = self._create_test_track(min_target_points)
        
        # Should work without errors
        interpolated = Track.interpolate_to_match_points(min_reference, min_target)
        
        self.assertEqual(len(interpolated.points), 2)
        self.assertAlmostEqual(interpolated.points[0].latitude, 0.000, places=6)
        self.assertAlmostEqual(interpolated.points[1].latitude, 0.001, places=6)
    
    def test_error_insufficient_points_reference(self):
        """Test error handling for insufficient points in reference track."""
        # Create track with only 1 point
        single_point = self._create_test_track([(0.0, 0.0, 100.0)])
        
        with self.assertRaises(ValueError) as context:
            Track.interpolate_to_match_points(single_point, self.target_track)
        
        self.assertIn("Reference track must have at least 2 points", str(context.exception))
    
    def test_error_insufficient_points_target(self):
        """Test error handling for insufficient points in target track."""
        # Create track with only 1 point
        single_point = self._create_test_track([(0.0, 0.0, 100.0)])
        
        with self.assertRaises(ValueError) as context:
            Track.interpolate_to_match_points(self.reference_track, single_point)
        
        self.assertIn("Target track must have at least 2 points", str(context.exception))
    
    def test_distance_preservation(self):
        """Test that total track distance is approximately preserved during interpolation."""
        interpolated = Track.interpolate_to_match_points(self.reference_track, self.target_track)
        
        original_distance = self.reference_track.total_distance
        interpolated_distance = interpolated.total_distance
        
        # Distance should be preserved within 1% tolerance
        relative_error = abs(original_distance - interpolated_distance) / original_distance
        self.assertLess(relative_error, 0.01, 
                       f"Distance preservation error too large: {relative_error:.4f}")
    
    def test_linear_interpolation_accuracy(self):
        """Test interpolation accuracy with a known linear path."""
        # Create a perfect linear track
        linear_points = [
            (0.000, 0.000, 100.0),
            (0.001, 0.001, 150.0),
            (0.002, 0.002, 200.0),
            (0.003, 0.003, 250.0)
        ]
        linear_track = self._create_test_track(linear_points)
        
        # Target with 7 points
        target_7pts = self._create_test_track([(0, 0, 0)] * 7)
        
        # Interpolate
        interpolated = Track.interpolate_to_match_points(linear_track, target_7pts)
        
        # For linear track, verify that interpolated points lie on the line y=x
        for point in interpolated.points:
            lat_lon_diff = abs(point.latitude - point.longitude)
            self.assertLess(lat_lon_diff, 1e-6, 
                           f"Point not on expected line: lat={point.latitude}, lon={point.longitude}")
            
            # Elevation should progress linearly
            self.assertGreaterEqual(point.elevation, 100.0)
            self.assertLessEqual(point.elevation, 250.0)
    
    def test_interpolation_with_curved_path(self):
        """Test interpolation with a curved path (simulated)."""
        # Create a curved path using sine function
        import numpy as np
        
        x_vals = np.linspace(0, 2*np.pi, 10)
        curved_points = []
        for i, x in enumerate(x_vals):
            lat = x * 0.001
            lon = math.sin(x) * 0.001
            elev = 100 + 50 * math.sin(x)
            curved_points.append((lat, lon, elev))
        
        curved_track = self._create_test_track(curved_points)
        
        # Target with different point count
        target_5pts = self._create_test_track([(0, 0, 0)] * 5)
        
        # Interpolate
        interpolated = Track.interpolate_to_match_points(curved_track, target_5pts)
        
        # Verify basic properties
        self.assertEqual(len(interpolated.points), 5)
        
        # Verify start and end are preserved
        self.assertAlmostEqual(interpolated.points[0].latitude, curved_track.points[0].latitude, places=6)
        self.assertAlmostEqual(interpolated.points[-1].latitude, curved_track.points[-1].latitude, places=6)


class TestGPXInterpolationIntegration(unittest.TestCase):
    """Integration tests for GPX interpolation with file operations."""
    
    def test_create_sample_gpx_content(self):
        """Test creating and interpolating with simulated GPX-like data."""
        # Simulate realistic GPS coordinates (around Zurich)
        realistic_points = [
            (47.3769, 8.5417, 408.0),
            (47.3770, 8.5420, 410.0),
            (47.3772, 8.5425, 415.0),
            (47.3775, 8.5430, 420.0),
            (47.3778, 8.5435, 425.0)
        ]
        
        subset_points = [
            (47.3769, 8.5417, 408.0),
            (47.3775, 8.5430, 420.0),
            (47.3778, 8.5435, 425.0)
        ]
        
        full_track = Track([Point(lat, lon, elev) for lat, lon, elev in realistic_points])
        subset_track = Track([Point(lat, lon, elev) for lat, lon, elev in subset_points])
        
        # Interpolate full track to match subset point count
        interpolated = Track.interpolate_to_match_points(full_track, subset_track)
        
        # Verify realistic coordinates are maintained
        self.assertEqual(len(interpolated.points), 3)
        
        # Check that coordinates are in reasonable range for Zurich
        for point in interpolated.points:
            self.assertGreater(point.latitude, 47.3)
            self.assertLess(point.latitude, 47.4)
            self.assertGreater(point.longitude, 8.5)
            self.assertLess(point.longitude, 8.6)
            self.assertGreater(point.elevation, 400)
            self.assertLess(point.elevation, 450)


if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTest(unittest.makeSuite(TestGPXInterpolation))
    suite.addTest(unittest.makeSuite(TestGPXInterpolationIntegration))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)