"""
Simple tests for GPX Track interpolation functionality without external dependencies.

This module tests the Track.interpolate_to_match_points() method using synthetic test data
that doesn't require loading actual GPX files or external geospatial libraries.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Mock the external dependencies
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

# Monkey patch the imports
import sys
sys.modules['pygeodesy'] = type('module', (), {'GeoidKarney': MockGeoidKarney})()
sys.modules['pygeodesy.ellipsoidalKarney'] = type('module', (), {'LatLon': MockLatLon})()
sys.modules['gpxpy'] = MockGpxpy()

# Now import our models
from src.gpx_dataengine.models import Track, Point


def create_test_track(points_data):
    """Helper function to create a Track from list of (lat, lon, elev) tuples."""
    points = [Point(lat, lon, elev) for lat, lon, elev in points_data]
    return Track(points)


def test_basic_interpolation():
    """Test basic interpolation functionality."""
    print("=" * 60)
    print("TEST 1: Basic interpolation functionality")
    print("=" * 60)
    
    # Create a simple reference track with 5 points (straight line)
    reference_points = [
        (0.0, 0.0, 100.0),
        (0.001, 0.001, 110.0),
        (0.002, 0.002, 120.0),
        (0.003, 0.003, 130.0),
        (0.004, 0.004, 140.0)
    ]
    reference_track = create_test_track(reference_points)
    
    # Create target track with 3 points
    target_points = [
        (0.0, 0.0, 0.0),
        (0.002, 0.002, 0.0),  
        (0.004, 0.004, 0.0)
    ]
    target_track = create_test_track(target_points)
    
    # Perform interpolation
    interpolated_track = Track.interpolate_to_match_points(reference_track, target_track)
    
    # Verify results
    print(f"Reference track points: {len(reference_track.points)}")
    print(f"Target track points: {len(target_track.points)}")
    print(f"Interpolated track points: {len(interpolated_track.points)}")
    
    assert len(interpolated_track.points) == len(target_track.points), "Point count mismatch"
    
    # Check interpolated points
    for i, point in enumerate(interpolated_track.points):
        print(f"Point {i}: ({point.latitude:.6f}, {point.longitude:.6f}, {point.elevation:.1f})")
    
    # Verify first and last points are preserved (approximately)
    first_ref = reference_track.points[0]
    last_ref = reference_track.points[-1]
    first_interp = interpolated_track.points[0]
    last_interp = interpolated_track.points[-1]
    
    assert abs(first_ref.latitude - first_interp.latitude) < 1e-6, "First latitude not preserved"
    assert abs(first_ref.longitude - first_interp.longitude) < 1e-6, "First longitude not preserved"
    assert abs(last_ref.latitude - last_interp.latitude) < 1e-6, "Last latitude not preserved"
    assert abs(last_ref.longitude - last_interp.longitude) < 1e-6, "Last longitude not preserved"
    
    print("✓ Basic interpolation test passed")
    print()


def test_upsampling():
    """Test upsampling (fewer to more points)."""
    print("=" * 60)
    print("TEST 2: Upsampling test")
    print("=" * 60)
    
    # 3-point reference track
    reference_points = [
        (0.0, 0.0, 100.0),
        (0.002, 0.002, 120.0),
        (0.004, 0.004, 140.0)
    ]
    reference_track = create_test_track(reference_points)
    
    # Target with 6 points
    target_track = create_test_track([(0, 0, 0)] * 6)
    
    # Interpolate
    interpolated = Track.interpolate_to_match_points(reference_track, target_track)
    
    print(f"Upsampling: {len(reference_track.points)} -> {len(interpolated.points)} points")
    
    assert len(interpolated.points) == 6, "Upsampling failed"
    
    # Check that interpolated points follow expected pattern
    for i, point in enumerate(interpolated.points):
        print(f"Point {i}: ({point.latitude:.6f}, {point.longitude:.6f}, {point.elevation:.1f})")
        
        # Points should lie roughly on the line y=x with elevation 100-140
        assert abs(point.latitude - point.longitude) < 1e-5, f"Point {i} not on expected line"
        assert 100 <= point.elevation <= 140, f"Point {i} elevation out of range"
    
    print("✓ Upsampling test passed")
    print()


def test_downsampling():
    """Test downsampling (more to fewer points)."""
    print("=" * 60)
    print("TEST 3: Downsampling test")
    print("=" * 60)
    
    # 8-point reference track
    reference_points = []
    for i in range(8):
        lat = i * 0.001
        lon = i * 0.001
        elev = 100 + i * 10
        reference_points.append((lat, lon, elev))
    
    reference_track = create_test_track(reference_points)
    
    # Target with 4 points
    target_track = create_test_track([(0, 0, 0)] * 4)
    
    # Interpolate
    interpolated = Track.interpolate_to_match_points(reference_track, target_track)
    
    print(f"Downsampling: {len(reference_track.points)} -> {len(interpolated.points)} points")
    
    assert len(interpolated.points) == 4, "Downsampling failed"
    
    for i, point in enumerate(interpolated.points):
        print(f"Point {i}: ({point.latitude:.6f}, {point.longitude:.6f}, {point.elevation:.1f})")
    
    print("✓ Downsampling test passed")
    print()


def test_edge_cases():
    """Test edge cases."""
    print("=" * 60)
    print("TEST 4: Edge cases")
    print("=" * 60)
    
    # Test with None elevations
    ref_points = [(0.0, 0.0, None), (0.001, 0.001, None)]
    target_points = [(0.0, 0.0, 0.0), (0.001, 0.001, 0.0)]
    
    ref_track = create_test_track(ref_points)
    target_track = create_test_track(target_points)
    
    interpolated = Track.interpolate_to_match_points(ref_track, target_track)
    
    print(f"None elevation test: {len(interpolated.points)} points")
    for point in interpolated.points:
        print(f"Elevation: {point.elevation}")
        assert point.elevation is None, "None elevations not preserved"
    
    # Test error condition: single point
    single_point_track = create_test_track([(0.0, 0.0, 100.0)])
    try:
        Track.interpolate_to_match_points(single_point_track, target_track)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Correctly caught error: {e}")
    
    print("✓ Edge cases test passed")
    print()


def run_simple_tests():
    """Run all simple tests."""
    print("Starting simple GPX interpolation tests...")
    print("(Note: These tests use mocked dependencies)")
    print()
    
    try:
        test_basic_interpolation()
        test_upsampling()
        test_downsampling()
        test_edge_cases()
        
        print("=" * 60)
        print("ALL SIMPLE TESTS PASSED! ✓")
        print("=" * 60)
        print()
        print("The interpolation function works correctly with synthetic data.")
        print("For full testing with real GPX files, install required dependencies:")
        print("  pip install pygeodesy gpxpy scipy numpy matplotlib")
        
    except Exception as e:
        print(f"TEST SUITE FAILED: {e}")
        raise


if __name__ == "__main__":
    run_simple_tests()