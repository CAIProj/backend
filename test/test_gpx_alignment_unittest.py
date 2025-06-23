"""
Unit tests for GPX Track alignment functionality using unittest framework.

This module contains proper unit tests that can be run with standard Python test runners.
Run with: python -m unittest test.test_gpx_alignment_unittest
Or: python -m pytest test/test_gpx_alignment_unittest.py
"""

import unittest
import sys
import os
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


class TestGPXAlignment(unittest.TestCase):
    """Test cases for GPX Track alignment functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Standard test tracks for alignment testing
        self.perfect_track1_points = [
            (0.000, 0.000, 100.0),
            (0.001, 0.001, 110.0),
            (0.002, 0.002, 120.0),
            (0.003, 0.003, 130.0),
            (0.004, 0.004, 140.0)
        ]
        
        self.perfect_track2_points = [
            (0.000, 0.000, 200.0),
            (0.0005, 0.0015, 210.0),
            (0.0015, 0.0025, 220.0),
            (0.004, 0.004, 240.0)
        ]
        
        self.perfect_track1 = self._create_test_track(self.perfect_track1_points)
        self.perfect_track2 = self._create_test_track(self.perfect_track2_points)
    
    def _create_test_track(self, points_data):
        """Helper method to create a Track from list of (lat, lon, elev) tuples."""
        points = [Point(lat, lon, elev) for lat, lon, elev in points_data]
        return Track(points)
    
    def test_perfect_alignment(self):
        """Test alignment when tracks already have identical start/end points."""
        # Create tracks with identical start and end points
        aligned1, aligned2 = Track.align_track_endpoints(self.perfect_track1, self.perfect_track2)
        
        # Verify tracks are returned (not None)
        self.assertIsNotNone(aligned1)
        self.assertIsNotNone(aligned2)
        
        # Verify point counts
        self.assertGreater(len(aligned1.points), 0)
        self.assertGreater(len(aligned2.points), 0)
        
        # Verify start and end points are aligned within tolerance
        start_distance = aligned1.points[0].distance_to(aligned2.points[0])
        end_distance = aligned1.points[-1].distance_to(aligned2.points[-1])
        
        self.assertLess(start_distance, 0.1, "Start points not aligned within tolerance")
        self.assertLess(end_distance, 0.1, "End points not aligned within tolerance")
    
    def test_start_offset_alignment(self):
        """Test alignment when one track starts earlier than the other."""
        # Track 1 starts earlier (has extra points at beginning)
        track1_points = [
            (-0.002, -0.002, 80.0),  # Extra start points
            (-0.001, -0.001, 90.0),
            (0.000, 0.000, 100.0),   # Matching start
            (0.001, 0.001, 110.0),
            (0.002, 0.002, 120.0),
            (0.003, 0.003, 130.0)    # Matching end
        ]
        
        # Track 2 starts at the "middle" of track 1
        track2_points = [
            (0.000, 0.000, 200.0),   # Matching start
            (0.0005, 0.0015, 210.0),
            (0.0015, 0.0025, 220.0),
            (0.003, 0.003, 230.0)    # Matching end
        ]
        
        track1 = self._create_test_track(track1_points)
        track2 = self._create_test_track(track2_points)
        
        original_track1_length = len(track1.points)
        original_track2_length = len(track2.points)
        
        # Align tracks
        aligned1, aligned2 = Track.align_track_endpoints(track1, track2)
        
        # Verify track1 was truncated (started earlier)
        self.assertLess(len(aligned1.points), original_track1_length, 
                       "Track 1 should be truncated")
        
        # Verify track2 length unchanged or minimally changed
        self.assertLessEqual(len(aligned2.points), original_track2_length)
        
        # Verify alignment quality
        start_distance = aligned1.points[0].distance_to(aligned2.points[0])
        end_distance = aligned1.points[-1].distance_to(aligned2.points[-1])
        
        self.assertLess(start_distance, 0.1, "Start alignment failed")
        self.assertLess(end_distance, 0.1, "End alignment failed")
    
    def test_end_offset_alignment(self):
        """Test alignment when one track ends later than the other."""
        # Track 1 ends at a certain point
        track1_points = [
            (0.000, 0.000, 100.0),   # Matching start
            (0.001, 0.001, 110.0),
            (0.002, 0.002, 120.0),
            (0.003, 0.003, 130.0)    # Matching end
        ]
        
        # Track 2 continues beyond track 1
        track2_points = [
            (0.000, 0.000, 200.0),   # Matching start
            (0.0005, 0.0015, 210.0),
            (0.0015, 0.0025, 220.0),
            (0.003, 0.003, 230.0),   # Matching end
            (0.004, 0.004, 240.0),   # Extra end points
            (0.005, 0.005, 250.0)
        ]
        
        track1 = self._create_test_track(track1_points)
        track2 = self._create_test_track(track2_points)
        
        original_track1_length = len(track1.points)
        original_track2_length = len(track2.points)
        
        # Align tracks
        aligned1, aligned2 = Track.align_track_endpoints(track1, track2)
        
        # Verify track2 was truncated (ended later)
        self.assertLess(len(aligned2.points), original_track2_length, 
                       "Track 2 should be truncated")
        
        # Verify track1 length unchanged or minimally changed
        self.assertLessEqual(len(aligned1.points), original_track1_length)
        
        # Verify alignment quality
        start_distance = aligned1.points[0].distance_to(aligned2.points[0])
        end_distance = aligned1.points[-1].distance_to(aligned2.points[-1])
        
        self.assertLess(start_distance, 0.1, "Start alignment failed")
        self.assertLess(end_distance, 0.1, "End alignment failed")
    
    def test_both_offsets_alignment(self):
        """Test alignment when both tracks have different start and end points."""
        # Track 1: starts early, ends early
        track1_points = [
            (-0.001, -0.001, 90.0),  # Extra start
            (0.000, 0.000, 100.0),   # Matching start
            (0.001, 0.001, 110.0),
            (0.002, 0.002, 120.0)    # Matching end
        ]
        
        # Track 2: starts late, ends late  
        track2_points = [
            (0.000, 0.000, 200.0),   # Matching start
            (0.0005, 0.0015, 210.0),
            (0.0015, 0.0025, 220.0),
            (0.002, 0.002, 230.0),   # Matching end
            (0.003, 0.003, 240.0)    # Extra end
        ]
        
        track1 = self._create_test_track(track1_points)
        track2 = self._create_test_track(track2_points)
        
        original_track1_length = len(track1.points)
        original_track2_length = len(track2.points)
        
        # Align tracks
        aligned1, aligned2 = Track.align_track_endpoints(track1, track2)
        
        # Both tracks should be truncated
        self.assertLess(len(aligned1.points), original_track1_length, 
                       "Track 1 should be truncated")
        self.assertLess(len(aligned2.points), original_track2_length, 
                       "Track 2 should be truncated")
        
        # Verify alignment quality
        start_distance = aligned1.points[0].distance_to(aligned2.points[0])
        end_distance = aligned1.points[-1].distance_to(aligned2.points[-1])
        
        self.assertLess(start_distance, 0.1, "Start alignment failed")
        self.assertLess(end_distance, 0.1, "End alignment failed")
    
    def test_tolerance_strict(self):
        """Test alignment with strict tolerance settings."""
        # Create tracks with points ~50m apart
        track1_points = [
            (0.000, 0.000, 100.0),
            (0.001, 0.001, 110.0),
            (0.002, 0.002, 120.0)
        ]
        
        # Track 2 has points ~50m away (0.00045 degrees ≈ 50m)
        track2_points = [
            (0.00045, 0.00045, 200.0),
            (0.0015, 0.0015, 210.0),
            (0.00245, 0.00245, 220.0)
        ]
        
        track1 = self._create_test_track(track1_points)
        track2 = self._create_test_track(track2_points)
        
        # Test with very strict tolerance (should fail)
        with self.assertRaises(ValueError) as context:
            Track.align_track_endpoints(track1, track2, tolerance_km=0.01)  # 10m tolerance
        
        self.assertIn("Cannot find matching", str(context.exception))
    
    def test_tolerance_loose(self):
        """Test alignment with loose tolerance settings."""
        # Create tracks with points ~50m apart
        track1_points = [
            (0.000, 0.000, 100.0),
            (0.001, 0.001, 110.0),
            (0.002, 0.002, 120.0)
        ]
        
        # Track 2 has points ~50m away
        track2_points = [
            (0.00045, 0.00045, 200.0),
            (0.0015, 0.0015, 210.0),
            (0.00245, 0.00245, 220.0)
        ]
        
        track1 = self._create_test_track(track1_points)
        track2 = self._create_test_track(track2_points)
        
        # Test with loose tolerance (should succeed)
        aligned1, aligned2 = Track.align_track_endpoints(track1, track2, tolerance_km=0.1)  # 100m tolerance
        
        # Verify alignment succeeded
        self.assertIsNotNone(aligned1)
        self.assertIsNotNone(aligned2)
        
        # Verify distances are within tolerance
        start_distance = aligned1.points[0].distance_to(aligned2.points[0])
        end_distance = aligned1.points[-1].distance_to(aligned2.points[-1])
        
        self.assertLessEqual(start_distance, 0.1)
        self.assertLessEqual(end_distance, 0.1)
    
    def test_error_insufficient_points_track1(self):
        """Test error handling for insufficient points in track1."""
        single_point_track = self._create_test_track([(0.0, 0.0, 100.0)])
        
        with self.assertRaises(ValueError) as context:
            Track.align_track_endpoints(single_point_track, self.perfect_track2)
        
        self.assertIn("Both tracks must have at least 2 points", str(context.exception))
    
    def test_error_insufficient_points_track2(self):
        """Test error handling for insufficient points in track2."""
        single_point_track = self._create_test_track([(0.0, 0.0, 100.0)])
        
        with self.assertRaises(ValueError) as context:
            Track.align_track_endpoints(self.perfect_track1, single_point_track)
        
        self.assertIn("Both tracks must have at least 2 points", str(context.exception))
    
    def test_error_no_matching_points(self):
        """Test error handling when tracks are too far apart."""
        # Create tracks very far apart (different continents)
        track1_points = [
            (47.3769, 8.5417, 100.0),  # Zurich
            (47.3770, 8.5420, 110.0),
            (47.3772, 8.5425, 120.0)
        ]
        
        track2_points = [
            (40.7128, -74.0060, 200.0),  # New York (very far away)
            (40.7130, -74.0058, 210.0),
            (40.7132, -74.0056, 220.0)
        ]
        
        track1 = self._create_test_track(track1_points)
        track2 = self._create_test_track(track2_points)
        
        with self.assertRaises(ValueError) as context:
            Track.align_track_endpoints(track1, track2, tolerance_km=0.1)
        
        self.assertIn("Cannot find matching", str(context.exception))
    
    def test_minimum_valid_tracks(self):
        """Test alignment with minimum valid tracks (2 points each)."""
        track1_points = [(0.000, 0.000, 100.0), (0.001, 0.001, 110.0)]
        track2_points = [(0.000, 0.000, 200.0), (0.001, 0.001, 210.0)]
        
        track1 = self._create_test_track(track1_points)
        track2 = self._create_test_track(track2_points)
        
        # Should work without errors
        aligned1, aligned2 = Track.align_track_endpoints(track1, track2)
        
        self.assertEqual(len(aligned1.points), 2)
        self.assertEqual(len(aligned2.points), 2)
        
        # Verify perfect alignment
        start_distance = aligned1.points[0].distance_to(aligned2.points[0])
        end_distance = aligned1.points[-1].distance_to(aligned2.points[-1])
        
        self.assertAlmostEqual(start_distance, 0.0, places=6)
        self.assertAlmostEqual(end_distance, 0.0, places=6)
    
    def test_realistic_gps_scenario(self):
        """Test alignment with realistic GPS recording scenario."""
        # Simulate realistic GPS tracks of same route started/stopped at different times
        base_route = [
            (47.3769, 8.5417, 408.0),  # Zurich coordinates
            (47.3770, 8.5420, 410.0),
            (47.3772, 8.5425, 415.0),
            (47.3775, 8.5430, 420.0),
            (47.3778, 8.5435, 425.0),
            (47.3780, 8.5440, 430.0)
        ]
        
        # Recording 1: Started early, ended at exact finish
        recording1_points = [
            (47.3766, 8.5410, 400.0),  # Started early
            (47.3767, 8.5413, 405.0),
        ] + base_route[1:]  # Main route
        
        # Recording 2: Started at exact start, ended late
        recording2_points = base_route + [
            (47.3782, 8.5445, 435.0),  # Ended late
            (47.3785, 8.5450, 440.0)
        ]
        
        track1 = self._create_test_track(recording1_points)
        track2 = self._create_test_track(recording2_points)
        
        original_start_dist = track1.points[0].distance_to(track2.points[0])
        original_end_dist = track1.points[-1].distance_to(track2.points[-1])
        
        # Align with realistic tolerance (200m)
        aligned1, aligned2 = Track.align_track_endpoints(track1, track2, tolerance_km=0.2)
        
        aligned_start_dist = aligned1.points[0].distance_to(aligned2.points[0])
        aligned_end_dist = aligned1.points[-1].distance_to(aligned2.points[-1])
        
        # Verify improvements
        self.assertLess(aligned_start_dist, original_start_dist, "Start alignment should improve")
        self.assertLess(aligned_end_dist, original_end_dist, "End alignment should improve")
        self.assertLessEqual(aligned_start_dist, 0.2, "Start points should be within tolerance")
        self.assertLessEqual(aligned_end_dist, 0.2, "End points should be within tolerance")
    
    def test_search_efficiency(self):
        """Test that alignment searches within reasonable bounds (first/last 20%)."""
        # Create a long track where only the middle points could match
        long_track_points = []
        for i in range(20):  # 20 points
            lat = i * 0.001
            lon = i * 0.001
            elev = 100 + i * 5
            long_track_points.append((lat, lon, elev))
        
        # Short track that matches points 8-12 of the long track (middle section)
        short_track_points = [
            (0.008, 0.008, 140.0),  # Matches point 8
            (0.010, 0.010, 150.0),  # Matches point 10
            (0.012, 0.012, 160.0)   # Matches point 12
        ]
        
        long_track = self._create_test_track(long_track_points)
        short_track = self._create_test_track(short_track_points)
        
        # The algorithm should NOT find the middle matches because it only searches
        # the first/last 20% of each track. This should raise an error.
        with self.assertRaises(ValueError) as context:
            Track.align_track_endpoints(long_track, short_track, tolerance_km=0.1)
        
        self.assertIn("Cannot find matching", str(context.exception))


class TestGPXAlignmentIntegration(unittest.TestCase):
    """Integration tests for GPX alignment with combined workflows."""
    
    def test_alignment_followed_by_interpolation(self):
        """Test complete workflow: alignment followed by interpolation."""
        # Create tracks with different start/end points and different point counts
        track1_points = [
            (-0.001, -0.001, 90.0),   # Extra start
            (0.000, 0.000, 100.0),
            (0.001, 0.001, 110.0),
            (0.002, 0.002, 120.0),
            (0.003, 0.003, 130.0)
        ]
        
        track2_points = [
            (0.000, 0.000, 200.0),
            (0.0015, 0.0015, 220.0),
            (0.003, 0.003, 240.0),
            (0.004, 0.004, 250.0)      # Extra end
        ]
        
        track1 = Track([Point(lat, lon, elev) for lat, lon, elev in track1_points])
        track2 = Track([Point(lat, lon, elev) for lat, lon, elev in track2_points])
        
        # Step 1: Align endpoints
        aligned1, aligned2 = Track.align_track_endpoints(track1, track2, tolerance_km=0.1)
        
        # Verify alignment worked
        self.assertGreater(len(aligned1.points), 0)
        self.assertGreater(len(aligned2.points), 0)
        
        # Step 2: Interpolate to same point count
        if len(aligned1.points) != len(aligned2.points):
            if len(aligned1.points) > len(aligned2.points):
                final1 = Track.interpolate_to_match_points(aligned1, aligned2)
                final2 = aligned2
            else:
                final1 = aligned1
                final2 = Track.interpolate_to_match_points(aligned2, aligned1)
        else:
            final1, final2 = aligned1, aligned2
        
        # Verify final result: same point count and aligned endpoints
        self.assertEqual(len(final1.points), len(final2.points))
        
        start_distance = final1.points[0].distance_to(final2.points[0])
        end_distance = final1.points[-1].distance_to(final2.points[-1])
        
        self.assertLess(start_distance, 0.1, "Final tracks should have aligned starts")
        self.assertLess(end_distance, 0.1, "Final tracks should have aligned ends")


if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTest(unittest.makeSuite(TestGPXAlignment))
    suite.addTest(unittest.makeSuite(TestGPXAlignmentIntegration))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)