"""
Unit tests for GPX Track interpolation functionality - CORRECTED VERSION.

This module tests the corrected implementation that interpolates the FIRST recording (full route)
to match the number of points in the SECOND recording (subset).

Test the exact task: "interpolate the points in the second recording for comparison purposes, 
so that the number of recorded points is the same in both recordings"

Run with: python test/test_gpx_interpolation_corrected.py
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


class TestGPXInterpolationCorrected(unittest.TestCase):
    """Test cases for the corrected GPX Track interpolation functionality."""
    
    def setUp(self):
        """Set up test fixtures demonstrating the exact task scenario."""
        
        # SCENARIO: Full route with 6 points (complete recording)
        self.full_route_points = [
            (47.3769, 8.5417, 408.0),  # Start of route
            (47.3770, 8.5420, 410.0),  # Point along route
            (47.3772, 8.5425, 415.0),  # Point along route
            (47.3775, 8.5430, 420.0),  # Point along route
            (47.3778, 8.5435, 425.0),  # Point along route
            (47.3780, 8.5440, 430.0)   # End of route
        ]
        
        # SCENARIO: Subset route with 3 points (partial recording of same route)
        self.subset_route_points = [
            (47.3769, 8.5417, 408.0),  # Same start
            (47.3775, 8.5430, 420.0),  # Middle point
            (47.3780, 8.5440, 430.0)   # Same end
        ]
        
        self.full_route = self._create_test_track(self.full_route_points)
        self.subset_route = self._create_test_track(self.subset_route_points)
    
    def _create_test_track(self, points_data):
        """Helper method to create a Track from list of (lat, lon, elev) tuples."""
        points = [Point(lat, lon, elev) for lat, lon, elev in points_data]
        return Track(points)
    
    def test_task_exact_scenario(self):
        """
        Test the exact scenario described in the task:
        - Full route recording: 6 points
        - Subset recording: 3 points
        - Result: Full route interpolated to 3 points to match subset
        """
        print("\n" + "="*70)
        print("TEST: Exact Task Scenario")
        print("="*70)
        print(f"Full route has {len(self.full_route.points)} points")
        print(f"Subset route has {len(self.subset_route.points)} points")
        
        # Apply the task: interpolate FIRST recording to match SECOND recording's point count
        interpolated_full_route = Track.interpolate_to_match_points(self.full_route, self.subset_route)
        
        print(f"Interpolated full route now has {len(interpolated_full_route.points)} points")
        
        # VERIFY: The result should have the same number of points as the subset
        self.assertEqual(len(interpolated_full_route.points), len(self.subset_route.points),
                        "Interpolated full route should match subset point count")
        
        # VERIFY: Start and end points should be preserved from full route
        self.assertAlmostEqual(interpolated_full_route.points[0].latitude, 
                              self.full_route.points[0].latitude, places=6,
                              msg="Start latitude should be preserved")
        self.assertAlmostEqual(interpolated_full_route.points[-1].latitude, 
                              self.full_route.points[-1].latitude, places=6,
                              msg="End latitude should be preserved")
        
        print("✓ Task requirement satisfied: Full route interpolated to match subset point count")
        
        # Show the result
        print("\nOriginal full route points:")
        for i, point in enumerate(self.full_route.points):
            print(f"  {i}: ({point.latitude:.6f}, {point.longitude:.6f}, {point.elevation:.1f})")
        
        print("\nSubset route points (determines target count):")
        for i, point in enumerate(self.subset_route.points):
            print(f"  {i}: ({point.latitude:.6f}, {point.longitude:.6f}, {point.elevation:.1f})")
            
        print("\nInterpolated full route (now matches subset count):")
        for i, point in enumerate(interpolated_full_route.points):
            print(f"  {i}: ({point.latitude:.6f}, {point.longitude:.6f}, {point.elevation:.1f})")
        
        print("\n✓ SUCCESS: Both recordings now have the same number of points for comparison")
    
    def test_parameter_order_verification(self):
        """
        Test that the function parameters are in the correct order as per task description.
        """
        print("\n" + "="*70)
        print("TEST: Parameter Order Verification")
        print("="*70)
        
        # Create a longer route (10 points) and shorter subset (4 points)
        long_route_points = []
        for i in range(10):
            lat = 47.3769 + i * 0.0001
            lon = 8.5417 + i * 0.0001
            elev = 408.0 + i * 2
            long_route_points.append((lat, lon, elev))
        
        short_subset_points = [
            long_route_points[0],   # Start
            long_route_points[3],   # 1/3 through
            long_route_points[6],   # 2/3 through
            long_route_points[9]    # End
        ]
        
        long_route = self._create_test_track(long_route_points)
        short_subset = self._create_test_track(short_subset_points)
        
        print(f"Long route: {len(long_route.points)} points")
        print(f"Short subset: {len(short_subset.points)} points")
        
        # The task: interpolate FIRST parameter (long route) to match SECOND parameter (short subset)
        result = Track.interpolate_to_match_points(long_route, short_subset)
        
        print(f"Result: {len(result.points)} points")
        
        # Verify the first parameter was interpolated to match the second parameter's count
        self.assertEqual(len(result.points), len(short_subset.points),
                        "First parameter should be interpolated to match second parameter's point count")
        
        print("✓ Parameter order is correct: interpolate_to_match_points(full_route, subset_route)")
    
    def test_realistic_gps_scenario(self):
        """
        Test with a realistic GPS recording scenario where a subset is truly a subset.
        """
        print("\n" + "="*70)
        print("TEST: Realistic GPS Subset Scenario")
        print("="*70)
        
        # SCENARIO: Someone recorded a full hiking trail (12 points)
        full_hiking_trail = [
            (47.3769, 8.5417, 408.0),  # Trailhead
            (47.3771, 8.5419, 412.0),  # Into forest
            (47.3773, 8.5422, 418.0),  # Stream crossing
            (47.3775, 8.5426, 425.0),  # Steep section start
            (47.3777, 8.5430, 435.0),  # Steep section middle
            (47.3779, 8.5434, 445.0),  # Steep section end
            (47.3781, 8.5438, 455.0),  # Ridge approach
            (47.3783, 8.5442, 465.0),  # Ridge
            (47.3785, 8.5446, 475.0),  # Viewpoint
            (47.3787, 8.5450, 485.0),  # Summit approach
            (47.3789, 8.5454, 495.0),  # Summit
            (47.3791, 8.5458, 505.0)   # Beyond summit
        ]
        
        # SCENARIO: Someone else only recorded key waypoints (5 points) of same route
        key_waypoints = [
            (47.3769, 8.5417, 408.0),  # Trailhead (same)
            (47.3775, 8.5426, 425.0),  # Steep section start (same)
            (47.3783, 8.5442, 465.0),  # Ridge (same)
            (47.3789, 8.5454, 495.0),  # Summit (same)
            (47.3791, 8.5458, 505.0)   # Beyond summit (same)
        ]
        
        full_trail = self._create_test_track(full_hiking_trail)
        waypoints = self._create_test_track(key_waypoints)
        
        print(f"Full hiking trail recording: {len(full_trail.points)} points")
        print(f"Key waypoints recording: {len(waypoints.points)} points")
        
        # Apply interpolation: make full trail have same point count as waypoints
        interpolated_trail = Track.interpolate_to_match_points(full_trail, waypoints)
        
        print(f"Interpolated full trail: {len(interpolated_trail.points)} points")
        
        # Verify the interpolation worked correctly
        self.assertEqual(len(interpolated_trail.points), len(waypoints.points))
        
        # Verify route boundaries are preserved
        self.assertAlmostEqual(interpolated_trail.points[0].elevation, 408.0, delta=1.0)
        self.assertAlmostEqual(interpolated_trail.points[-1].elevation, 505.0, delta=1.0)
        
        # Verify elevation progression makes sense (should generally increase)
        elevations = [p.elevation for p in interpolated_trail.points]
        self.assertLess(elevations[0], elevations[-1], "Elevation should increase from trailhead to summit")
        
        print("✓ Realistic GPS scenario handled correctly")
        
        # Show elevation profile comparison
        print("\nFull trail elevation profile (original 12 points):")
        for i, point in enumerate(full_trail.points):
            print(f"  Point {i:2d}: {point.elevation:.1f}m")
            
        print(f"\nWaypoints elevation profile ({len(waypoints.points)} points):")
        for i, point in enumerate(waypoints.points):
            print(f"  Point {i:2d}: {point.elevation:.1f}m")
            
        print(f"\nInterpolated trail elevation profile ({len(interpolated_trail.points)} points):")
        for i, point in enumerate(interpolated_trail.points):
            print(f"  Point {i:2d}: {point.elevation:.1f}m")
    
    def test_downsampling_scenario(self):
        """
        Test the typical use case: downsample a detailed route to match a simplified one.
        """
        print("\n" + "="*70)
        print("TEST: Downsampling Scenario (Detailed → Simplified)")
        print("="*70)
        
        # Create a detailed route (every 10 meters, 20 points)
        detailed_points = []
        for i in range(20):
            lat = 47.3769 + i * 0.00005  # Small increments
            lon = 8.5417 + i * 0.00005
            elev = 408.0 + i * 1.5  # Gradual elevation gain
            detailed_points.append((lat, lon, elev))
        
        # Create a simplified route (every 100 meters, 5 points)  
        simplified_points = [
            detailed_points[0],    # Start
            detailed_points[5],    # 1/4 way
            detailed_points[10],   # 1/2 way
            detailed_points[15],   # 3/4 way
            detailed_points[19]    # End
        ]
        
        detailed_route = self._create_test_track(detailed_points)
        simplified_route = self._create_test_track(simplified_points)
        
        print(f"Detailed route: {len(detailed_route.points)} points (high resolution)")
        print(f"Simplified route: {len(simplified_route.points)} points (low resolution)")
        
        # Task: Interpolate detailed route to match simplified route's point count
        interpolated_detailed = Track.interpolate_to_match_points(detailed_route, simplified_route)
        
        print(f"Interpolated detailed route: {len(interpolated_detailed.points)} points")
        
        # Verify downsampling
        self.assertEqual(len(interpolated_detailed.points), len(simplified_route.points))
        self.assertLess(len(interpolated_detailed.points), len(detailed_route.points))
        
        # Verify accuracy: interpolated points should be close to simplified points
        for i in range(len(simplified_route.points)):
            distance = interpolated_detailed.points[i].distance_to(simplified_route.points[i])
            self.assertLess(distance, 0.01, f"Point {i} should be close between interpolated and simplified")
        
        print("✓ Downsampling scenario works correctly")
    
    def test_upsampling_scenario(self):
        """
        Test the edge case: upsample a simple route to match a detailed one.
        """
        print("\n" + "="*70)
        print("TEST: Upsampling Scenario (Simple → Detailed)")
        print("="*70)
        
        # Create a simple route (3 points)
        simple_points = [
            (47.3769, 8.5417, 408.0),  # Start
            (47.3775, 8.5430, 420.0),  # Middle
            (47.3780, 8.5440, 430.0)   # End
        ]
        
        # Create a detailed route (8 points) representing the same path
        detailed_points = []
        for i in range(8):
            # Linear interpolation between start and end
            ratio = i / 7.0
            lat = 47.3769 + ratio * (47.3780 - 47.3769)
            lon = 8.5417 + ratio * (8.5440 - 8.5417)
            elev = 408.0 + ratio * (430.0 - 408.0)
            detailed_points.append((lat, lon, elev))
        
        simple_route = self._create_test_track(simple_points)
        detailed_route = self._create_test_track(detailed_points)
        
        print(f"Simple route: {len(simple_route.points)} points")
        print(f"Detailed route: {len(detailed_route.points)} points (target count)")
        
        # Task: Interpolate simple route to match detailed route's point count  
        interpolated_simple = Track.interpolate_to_match_points(simple_route, detailed_route)
        
        print(f"Interpolated simple route: {len(interpolated_simple.points)} points")
        
        # Verify upsampling
        self.assertEqual(len(interpolated_simple.points), len(detailed_route.points))
        self.assertGreater(len(interpolated_simple.points), len(simple_route.points))
        
        # Verify that start and end are preserved
        self.assertAlmostEqual(interpolated_simple.points[0].latitude, simple_route.points[0].latitude, places=6)
        self.assertAlmostEqual(interpolated_simple.points[-1].latitude, simple_route.points[-1].latitude, places=6)
        
        print("✓ Upsampling scenario works correctly")
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        print("\n" + "="*70)
        print("TEST: Error Handling")
        print("="*70)
        
        # Test insufficient points
        single_point = self._create_test_track([(47.0, 8.0, 400.0)])
        valid_route = self._create_test_track([(47.0, 8.0, 400.0), (47.1, 8.1, 450.0)])
        
        # Test first parameter with insufficient points
        with self.assertRaises(ValueError) as context:
            Track.interpolate_to_match_points(single_point, valid_route)
        
        self.assertIn("Full route must have at least 2 points", str(context.exception))
        print("✓ Error handling for insufficient points in full route")
        
        # Test second parameter with insufficient points
        with self.assertRaises(ValueError) as context:
            Track.interpolate_to_match_points(valid_route, single_point)
        
        self.assertIn("Subset route must have at least 2 points", str(context.exception))
        print("✓ Error handling for insufficient points in subset route")


class TestInterpolationWorkflow(unittest.TestCase):
    """Test the complete workflow for comparing two GPX recordings."""
    
    def _create_test_track(self, points_data):
        """Helper method to create a Track from list of (lat, lon, elev) tuples."""
        points = [Point(lat, lon, elev) for lat, lon, elev in points_data]
        return Track(points)
    
    def test_complete_comparison_workflow(self):
        """
        Test the complete workflow described in the task:
        1. Load two GPX recordings where one is a subset of the other
        2. Interpolate to match point counts  
        3. Enable direct comparison
        """
        print("\n" + "="*70)
        print("TEST: Complete GPX Comparison Workflow")
        print("="*70)
        
        # STEP 1: Load two recordings (simulated)
        full_route_points = [
            (47.3769, 8.5417, 408.0),  # Start
            (47.3770, 8.5420, 410.0),  # Point 1
            (47.3772, 8.5425, 415.0),  # Point 2
            (47.3775, 8.5430, 420.0),  # Point 3
            (47.3778, 8.5435, 425.0),  # Point 4
            (47.3780, 8.5440, 430.0),  # End
        ]
        
        subset_points = [
            (47.3769, 8.5417, 408.0),  # Start (same)
            (47.3775, 8.5430, 420.0),  # Middle
            (47.3780, 8.5440, 430.0),  # End (same)
        ]
        
        recording1_full = self._create_test_track(full_route_points)
        recording2_subset = self._create_test_track(subset_points)
        
        print(f"Recording 1 (full route): {len(recording1_full.points)} points")
        print(f"Recording 2 (subset): {len(recording2_subset.points)} points")
        
        # STEP 2: Apply the task - interpolate first recording to match second
        interpolated_recording1 = Track.interpolate_to_match_points(recording1_full, recording2_subset)
        
        print(f"Interpolated recording 1: {len(interpolated_recording1.points)} points")
        
        # STEP 3: Verify that direct comparison is now possible
        self.assertEqual(len(interpolated_recording1.points), len(recording2_subset.points),
                        "Both recordings should now have same point count")
        
        # STEP 4: Demonstrate comparison capabilities
        print("\nDirect point-by-point comparison now possible:")
        total_distance_difference = 0.0
        total_elevation_difference = 0.0
        
        for i in range(len(interpolated_recording1.points)):
            p1 = interpolated_recording1.points[i]
            p2 = recording2_subset.points[i]
            
            # Calculate differences
            distance_diff = p1.distance_to(p2) * 1000  # Convert to meters
            elevation_diff = abs(p1.elevation - p2.elevation)
            
            total_distance_difference += distance_diff
            total_elevation_difference += elevation_diff
            
            print(f"  Point {i}: Distance diff = {distance_diff:.1f}m, Elevation diff = {elevation_diff:.1f}m")
        
        print(f"\nSummary:")
        print(f"  Average distance difference: {total_distance_difference / len(interpolated_recording1.points):.1f}m")
        print(f"  Average elevation difference: {total_elevation_difference / len(interpolated_recording1.points):.1f}m")
        
        print("✓ Complete comparison workflow successful")
        print("✓ Task requirement fulfilled: Both recordings have same number of points for comparison")


if __name__ == '__main__':
    print("GPX Interpolation Testing - CORRECTED IMPLEMENTATION")
    print("="*70)
    print("Testing the exact task requirement:")
    print("'Interpolate the points in the FIRST recording to match the SECOND recording'")
    print("'so that the number of recorded points is the same in both recordings'")
    print("="*70)
    
    # Run the tests with maximum verbosity
    unittest.main(verbosity=2)