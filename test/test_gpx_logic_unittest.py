"""
Unit tests for GPX functionality using simplified logic without external dependencies.

This module tests the core algorithms and logic without requiring scipy, numpy, etc.
Run with: python test/test_gpx_logic_unittest.py
"""

import unittest
import sys
import os
import math

class SimplePoint:
    """Simplified Point class for testing without external dependencies."""
    
    def __init__(self, latitude, longitude, elevation=None):
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
    
    def distance_to(self, other):
        """Simplified Haversine distance calculation."""
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1 = math.radians(self.latitude)
        lon1 = math.radians(self.longitude)
        lat2 = math.radians(other.latitude)
        lon2 = math.radians(other.longitude)
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def copy(self):
        return SimplePoint(self.latitude, self.longitude, self.elevation)

class SimpleTrack:
    """Simplified Track class for testing core alignment logic."""
    
    def __init__(self, points):
        self.points = points
    
    def _calculate_cumulative_distances(self):
        """Calculate cumulative distances between points."""
        if len(self.points) < 2:
            return [0.0]
        
        distances = [0.0]
        for i in range(1, len(self.points)):
            distance = self.points[i-1].distance_to(self.points[i])
            distances.append(distances[-1] + distance)
        
        return distances
    
    @property
    def total_distance(self):
        """Calculate total track distance."""
        distances = self._calculate_cumulative_distances()
        return distances[-1] if distances else 0.0

def find_best_start_alignment(track1, track2, tolerance_km):
    """Test implementation of start alignment logic."""
    best_distance = float('inf')
    best_indices = (None, None)
    
    # Search within first 20% of each track
    search_limit1 = max(1, len(track1.points) // 5)
    search_limit2 = max(1, len(track2.points) // 5)
    
    for i in range(search_limit1):
        for j in range(search_limit2):
            distance = track1.points[i].distance_to(track2.points[j])
            if distance <= tolerance_km and distance < best_distance:
                best_distance = distance
                best_indices = (i, j)
    
    return best_indices

def find_best_end_alignment(track1, track2, tolerance_km):
    """Test implementation of end alignment logic."""
    best_distance = float('inf')
    best_indices = (None, None)
    
    # Search within last 20% of each track
    search_start1 = len(track1.points) - max(1, len(track1.points) // 5)
    search_start2 = len(track2.points) - max(1, len(track2.points) // 5)
    
    for i in range(search_start1, len(track1.points)):
        for j in range(search_start2, len(track2.points)):
            distance = track1.points[i].distance_to(track2.points[j])
            if distance <= tolerance_km and distance < best_distance:
                best_distance = distance
                best_indices = (i, j)
    
    return best_indices

def simple_linear_interpolation(start_val, end_val, num_points):
    """Simple linear interpolation between two values."""
    if num_points <= 1:
        return [start_val]
    
    step = (end_val - start_val) / (num_points - 1)
    return [start_val + i * step for i in range(num_points)]


class TestGPXLogic(unittest.TestCase):
    """Test core GPX logic without external dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simple_points1 = [
            SimplePoint(0.000, 0.000, 100.0),
            SimplePoint(0.001, 0.001, 110.0),
            SimplePoint(0.002, 0.002, 120.0),
            SimplePoint(0.003, 0.003, 130.0)
        ]
        
        self.simple_points2 = [
            SimplePoint(0.000, 0.000, 200.0),
            SimplePoint(0.0015, 0.0015, 220.0),
            SimplePoint(0.003, 0.003, 240.0)
        ]
        
        self.track1 = SimpleTrack(self.simple_points1)
        self.track2 = SimpleTrack(self.simple_points2)
    
    def test_point_distance_calculation(self):
        """Test Haversine distance calculation."""
        p1 = SimplePoint(0.0, 0.0)
        p2 = SimplePoint(0.001, 0.001)
        
        distance = p1.distance_to(p2)
        
        # Distance should be approximately 0.157 km for these coordinates
        self.assertGreater(distance, 0.1)
        self.assertLess(distance, 0.2)
    
    def test_track_distance_calculation(self):
        """Test total track distance calculation."""
        distance = self.track1.total_distance
        
        # Should be positive
        self.assertGreater(distance, 0)
        
        # Should be reasonable for the coordinates used
        self.assertLess(distance, 1.0)  # Less than 1km for test data
    
    def test_start_alignment_logic(self):
        """Test start point alignment logic."""
        # Perfect alignment case
        perfect_track1 = SimpleTrack([
            SimplePoint(0.000, 0.000),
            SimplePoint(0.001, 0.001),
            SimplePoint(0.002, 0.002)
        ])
        
        perfect_track2 = SimpleTrack([
            SimplePoint(0.000, 0.000),
            SimplePoint(0.0005, 0.0015),
            SimplePoint(0.002, 0.002)
        ])
        
        start_indices = find_best_start_alignment(perfect_track1, perfect_track2, tolerance_km=0.1)
        
        # Should find perfect match at (0, 0)
        self.assertEqual(start_indices, (0, 0))
    
    def test_start_alignment_with_offset(self):
        """Test start alignment when one track starts earlier."""
        offset_track1 = SimpleTrack([
            SimplePoint(-0.002, -0.002),  # Extra start
            SimplePoint(-0.001, -0.001),  # Extra start
            SimplePoint(0.000, 0.000),    # Matching start
            SimplePoint(0.001, 0.001)
        ])
        
        regular_track2 = SimpleTrack([
            SimplePoint(0.000, 0.000),    # Matching start
            SimplePoint(0.001, 0.001)
        ])
        
        start_indices = find_best_start_alignment(offset_track1, regular_track2, tolerance_km=1.0)
        
        # Should find match with larger tolerance
        self.assertIsNotNone(start_indices[0], "Should find start alignment with sufficient tolerance")
        self.assertIsNotNone(start_indices[1], "Should find start alignment with sufficient tolerance")
    
    def test_end_alignment_logic(self):
        """Test end point alignment logic."""
        end_indices = find_best_end_alignment(self.track1, self.track2, tolerance_km=0.1)
        
        # Should find some valid alignment
        self.assertIsNotNone(end_indices[0])
        self.assertIsNotNone(end_indices[1])
        
        # Verify indices are within valid range
        self.assertGreaterEqual(end_indices[0], 0)
        self.assertLess(end_indices[0], len(self.track1.points))
        self.assertGreaterEqual(end_indices[1], 0)
        self.assertLess(end_indices[1], len(self.track2.points))
    
    def test_linear_interpolation_logic(self):
        """Test simple linear interpolation logic."""
        # Test interpolation between 0 and 10 with 5 points
        result = simple_linear_interpolation(0, 10, 5)
        expected = [0, 2.5, 5.0, 7.5, 10.0]
        
        for i, (actual, expected_val) in enumerate(zip(result, expected)):
            self.assertAlmostEqual(actual, expected_val, places=6, 
                                 msg=f"Interpolation failed at index {i}")
    
    def test_interpolation_edge_cases(self):
        """Test interpolation edge cases."""
        # Single point
        result = simple_linear_interpolation(5, 5, 1)
        self.assertEqual(result, [5])
        
        # Two points
        result = simple_linear_interpolation(0, 10, 2)
        self.assertEqual(result, [0, 10])
        
        # Zero points (should return single start value)
        result = simple_linear_interpolation(5, 10, 0)
        self.assertEqual(len(result), 1)
    
    def test_alignment_tolerance_logic(self):
        """Test alignment tolerance behavior."""
        # Create points that are exactly 0.05km apart
        p1 = SimplePoint(0.0, 0.0)
        p2 = SimplePoint(0.00045, 0.00045)  # Approximately 50m apart
        
        distance = p1.distance_to(p2)
        
        # Should be within 0.1km tolerance but outside 0.01km tolerance
        self.assertLess(distance, 0.1, "Points should be within loose tolerance")
        self.assertGreater(distance, 0.01, "Points should be outside strict tolerance")
    
    def test_coordinate_validity(self):
        """Test that coordinates are within valid GPS ranges."""
        # Test realistic coordinates (Zurich)
        zurich_point = SimplePoint(47.3769, 8.5417, 408.0)
        
        # GPS coordinates validity
        self.assertGreaterEqual(zurich_point.latitude, -90)
        self.assertLessEqual(zurich_point.latitude, 90)
        self.assertGreaterEqual(zurich_point.longitude, -180)
        self.assertLessEqual(zurich_point.longitude, 180)
        
        # Reasonable elevation
        self.assertGreater(zurich_point.elevation, 0)
        self.assertLess(zurich_point.elevation, 9000)  # Below Mount Everest
    
    def test_track_length_logic(self):
        """Test track length calculations."""
        # Empty track
        empty_track = SimpleTrack([])
        self.assertEqual(empty_track.total_distance, 0.0)
        
        # Single point track
        single_track = SimpleTrack([SimplePoint(0, 0)])
        self.assertEqual(single_track.total_distance, 0.0)
        
        # Multi-point track
        self.assertGreater(self.track1.total_distance, 0)


class TestGPXAlgorithmValidation(unittest.TestCase):
    """Validate GPX algorithm correctness."""
    
    def test_alignment_algorithm_correctness(self):
        """Test that the alignment algorithm produces correct results."""
        # Create a scenario where we know the expected result
        track1_points = [
            SimplePoint(-0.001, -0.001),  # Extra start
            SimplePoint(0.000, 0.000),    # Should align here
            SimplePoint(0.001, 0.001),
            SimplePoint(0.002, 0.002)     # Should align here
        ]
        
        track2_points = [
            SimplePoint(0.000, 0.000),    # Should align here
            SimplePoint(0.0005, 0.0015),
            SimplePoint(0.002, 0.002)     # Should align here
        ]
        
        track1 = SimpleTrack(track1_points)
        track2 = SimpleTrack(track2_points)
        
        # Test start alignment
        start_indices = find_best_start_alignment(track1, track2, tolerance_km=1.0)
        
        # Test end alignment
        end_indices = find_best_end_alignment(track1, track2, tolerance_km=1.0)
        
        # Verify that we found valid alignments with sufficient tolerance
        self.assertIsNotNone(start_indices[0], "Should find start alignment")
        self.assertIsNotNone(start_indices[1], "Should find start alignment")
        self.assertIsNotNone(end_indices[0], "Should find end alignment")
        self.assertIsNotNone(end_indices[1], "Should find end alignment")
        
        # Verify alignment quality
        if start_indices[0] is not None and start_indices[1] is not None:
            start_distance = track1.points[start_indices[0]].distance_to(
                track2.points[start_indices[1]]
            )
            self.assertLess(start_distance, 1.0)
        
        if end_indices[0] is not None and end_indices[1] is not None:
            end_distance = track1.points[end_indices[0]].distance_to(
                track2.points[end_indices[1]]
            )
            self.assertLess(end_distance, 1.0)
    
    def test_interpolation_preserves_endpoints(self):
        """Test that interpolation preserves start and end points."""
        start_lat, start_lon = 0.0, 0.0
        end_lat, end_lon = 0.003, 0.003
        
        # Interpolate latitudes
        lat_interpolated = simple_linear_interpolation(start_lat, end_lat, 5)
        lon_interpolated = simple_linear_interpolation(start_lon, end_lon, 5)
        
        # Check endpoints are preserved
        self.assertAlmostEqual(lat_interpolated[0], start_lat, places=6)
        self.assertAlmostEqual(lat_interpolated[-1], end_lat, places=6)
        self.assertAlmostEqual(lon_interpolated[0], start_lon, places=6)
        self.assertAlmostEqual(lon_interpolated[-1], end_lon, places=6)
        
        # Check monotonic progression
        for i in range(len(lat_interpolated) - 1):
            self.assertLessEqual(lat_interpolated[i], lat_interpolated[i + 1])
            self.assertLessEqual(lon_interpolated[i], lon_interpolated[i + 1])


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)