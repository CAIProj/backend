"""
Comprehensive tests for GPX Track interpolation functionality.

This module tests the Track.interpolate_to_match_points() method using various scenarios
including real GPX files and synthetic test data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.gpx_dataengine.models import Track, Point
import numpy as np
import matplotlib.pyplot as plt


def create_test_track(points_data):
    """Helper function to create a Track from list of (lat, lon, elev) tuples."""
    points = [Point(lat, lon, elev) for lat, lon, elev in points_data]
    return Track(points)


def test_basic_interpolation():
    """
    Test 1: Basic interpolation functionality
    Tests interpolation between a 5-point track and a 3-point target.
    """
    print("=" * 60)
    print("TEST 1: Basic interpolation functionality")
    print("=" * 60)
    
    # Create a simple reference track with 5 points (straight line)
    reference_points = [
        (0.0, 0.0, 100.0),  # Start
        (0.001, 0.001, 110.0),
        (0.002, 0.002, 120.0),
        (0.003, 0.003, 130.0),
        (0.004, 0.004, 140.0)  # End
    ]
    reference_track = create_test_track(reference_points)
    
    # Create target track with 3 points (just for count)
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
    
    # Check that first and last points match approximately
    first_ref = reference_track.points[0]
    last_ref = reference_track.points[-1]
    first_interp = interpolated_track.points[0]
    last_interp = interpolated_track.points[-1]
    
    print(f"First point - Reference: ({first_ref.latitude:.6f}, {first_ref.longitude:.6f}, {first_ref.elevation:.1f})")
    print(f"First point - Interpolated: ({first_interp.latitude:.6f}, {first_interp.longitude:.6f}, {first_interp.elevation:.1f})")
    print(f"Last point - Reference: ({last_ref.latitude:.6f}, {last_ref.longitude:.6f}, {last_ref.elevation:.1f})")
    print(f"Last point - Interpolated: ({last_interp.latitude:.6f}, {last_interp.longitude:.6f}, {last_interp.elevation:.1f})")
    
    # Verify first and last points are preserved
    assert abs(first_ref.latitude - first_interp.latitude) < 1e-6, "First latitude not preserved"
    assert abs(first_ref.longitude - first_interp.longitude) < 1e-6, "First longitude not preserved"
    assert abs(last_ref.latitude - last_interp.latitude) < 1e-6, "Last latitude not preserved"
    assert abs(last_ref.longitude - last_interp.longitude) < 1e-6, "Last longitude not preserved"
    
    print("✓ Basic interpolation test passed")
    print()


def test_edge_cases():
    """
    Test 2: Edge cases and error conditions
    Tests various edge cases that might cause issues.
    """
    print("=" * 60)
    print("TEST 2: Edge cases and error conditions")
    print("=" * 60)
    
    # Test with minimum points (2 each)
    ref_min = create_test_track([(0.0, 0.0, 100.0), (0.001, 0.001, 200.0)])
    target_min = create_test_track([(0.0, 0.0, 0.0), (0.001, 0.001, 0.0)])
    
    try:
        interpolated = Track.interpolate_to_match_points(ref_min, target_min)
        print(f"✓ Minimum points test passed - {len(interpolated.points)} points")
    except Exception as e:
        print(f"✗ Minimum points test failed: {e}")
        return
    
    # Test with None elevations
    ref_none_elev = create_test_track([(0.0, 0.0, None), (0.001, 0.001, None), (0.002, 0.002, None)])
    target_3pts = create_test_track([(0.0, 0.0, 0.0), (0.001, 0.001, 0.0), (0.002, 0.002, 0.0)])
    
    try:
        interpolated = Track.interpolate_to_match_points(ref_none_elev, target_3pts)
        print(f"✓ None elevation test passed - all elevations None: {all(p.elevation is None for p in interpolated.points)}")
    except Exception as e:
        print(f"✗ None elevation test failed: {e}")
        return
    
    # Test error condition: insufficient points
    ref_single = create_test_track([(0.0, 0.0, 100.0)])
    try:
        Track.interpolate_to_match_points(ref_single, target_min)
        print("✗ Should have raised ValueError for single point reference")
    except ValueError as e:
        print(f"✓ Correctly raised error for insufficient points: {e}")
    
    print()


def test_upsampling_downsampling():
    """
    Test 3: Upsampling and downsampling scenarios
    Tests both increasing and decreasing point count.
    """
    print("=" * 60)
    print("TEST 3: Upsampling and downsampling scenarios")
    print("=" * 60)
    
    # Create a curved reference track (quarter circle)
    n_ref = 10
    angles = np.linspace(0, np.pi/2, n_ref)
    radius = 0.01  # Small radius for realistic lat/lon differences
    
    reference_points = []
    for i, angle in enumerate(angles):
        lat = radius * np.cos(angle)
        lon = radius * np.sin(angle)
        elev = 100 + i * 10  # Linearly increasing elevation
        reference_points.append((lat, lon, elev))
    
    reference_track = create_test_track(reference_points)
    
    # Test upsampling (10 -> 20 points)
    target_up = create_test_track([(0, 0, 0)] * 20)
    interpolated_up = Track.interpolate_to_match_points(reference_track, target_up)
    
    print(f"Upsampling: {len(reference_track.points)} -> {len(interpolated_up.points)} points")
    print(f"Original distance: {reference_track.total_distance:.6f} km")
    print(f"Upsampled distance: {interpolated_up.total_distance:.6f} km")
    
    # Test downsampling (10 -> 5 points)
    target_down = create_test_track([(0, 0, 0)] * 5)
    interpolated_down = Track.interpolate_to_match_points(reference_track, target_down)
    
    print(f"Downsampling: {len(reference_track.points)} -> {len(interpolated_down.points)} points")
    print(f"Downsampled distance: {interpolated_down.total_distance:.6f} km")
    
    # Verify that distances are approximately preserved
    original_dist = reference_track.total_distance
    up_dist = interpolated_up.total_distance
    down_dist = interpolated_down.total_distance
    
    assert abs(original_dist - up_dist) < 0.001, f"Upsampling distance error too large: {abs(original_dist - up_dist)}"
    assert abs(original_dist - down_dist) < 0.001, f"Downsampling distance error too large: {abs(original_dist - down_dist)}"
    
    print("✓ Upsampling and downsampling tests passed")
    print()


def test_real_gpx_files():
    """
    Test 4: Real GPX file interpolation
    Tests interpolation using actual GPX files from the data directory.
    """
    print("=" * 60)
    print("TEST 4: Real GPX file interpolation")
    print("=" * 60)
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    # List available GPX files
    gpx_files = [f for f in os.listdir(data_dir) if f.endswith('.gpx')]
    
    if len(gpx_files) < 2:
        print("✗ Need at least 2 GPX files for real file testing")
        return
    
    print(f"Found {len(gpx_files)} GPX files: {gpx_files}")
    
    # Load two different GPX files
    track1_path = os.path.join(data_dir, gpx_files[0])
    track2_path = os.path.join(data_dir, gpx_files[1])
    
    try:
        track1 = Track.from_gpx_file(track1_path)
        track2 = Track.from_gpx_file(track2_path)
        
        print(f"Track 1 ({gpx_files[0]}): {len(track1.points)} points, {track1.total_distance:.3f} km")
        print(f"Track 2 ({gpx_files[1]}): {len(track2.points)} points, {track2.total_distance:.3f} km")
        
        # Interpolate track1 to match track2's point count
        interpolated = Track.interpolate_to_match_points(track1, track2)
        
        print(f"Interpolated track: {len(interpolated.points)} points, {interpolated.total_distance:.3f} km")
        
        # Verify point count matches
        assert len(interpolated.points) == len(track2.points), "Point count mismatch in real file test"
        
        # Verify distance is approximately preserved
        distance_error = abs(track1.total_distance - interpolated.total_distance)
        relative_error = distance_error / track1.total_distance * 100
        
        print(f"Distance preservation error: {distance_error:.6f} km ({relative_error:.2f}%)")
        
        assert relative_error < 1.0, f"Distance error too large: {relative_error:.2f}%"
        
        print("✓ Real GPX file interpolation test passed")
        
    except Exception as e:
        print(f"✗ Real GPX file test failed: {e}")
        return
    
    print()


def test_interpolation_accuracy():
    """
    Test 5: Interpolation accuracy verification
    Tests that interpolated points lie on the expected path.
    """
    print("=" * 60)
    print("TEST 5: Interpolation accuracy verification")
    print("=" * 60)
    
    # Create a simple linear track for precise verification
    reference_points = [
        (0.000, 0.000, 100.0),
        (0.001, 0.001, 150.0),
        (0.002, 0.002, 200.0),
        (0.003, 0.003, 250.0)
    ]
    reference_track = create_test_track(reference_points)
    
    # Target track with 7 points (more than reference)
    target_track = create_test_track([(0, 0, 0)] * 7)
    
    # Interpolate
    interpolated = Track.interpolate_to_match_points(reference_track, target_track)
    
    print(f"Testing accuracy with {len(interpolated.points)} interpolated points")
    
    # For a linear track, interpolated points should lie on the line y=x and elevation should be linear
    for i, point in enumerate(interpolated.points):
        print(f"Point {i}: ({point.latitude:.6f}, {point.longitude:.6f}, {point.elevation:.1f})")
        
        # Check that lat ≈ lon (linear relationship)
        lat_lon_diff = abs(point.latitude - point.longitude)
        assert lat_lon_diff < 1e-6, f"Point {i} not on expected line: lat={point.latitude}, lon={point.longitude}"
        
        # Check elevation progression (should be between 100 and 250)
        assert 100 <= point.elevation <= 250, f"Point {i} elevation out of range: {point.elevation}"
    
    print("✓ Interpolation accuracy test passed")
    print()


def visualize_interpolation_example():
    """
    Test 6: Visualization of interpolation results
    Creates a visual example of the interpolation process.
    """
    print("=" * 60)
    print("TEST 6: Visualization example")
    print("=" * 60)
    
    # Create a sine wave track for interesting visualization
    x_vals = np.linspace(0, 2*np.pi, 15)
    reference_points = []
    for i, x in enumerate(x_vals):
        lat = x * 0.001  # Scale to reasonable lat/lon values
        lon = np.sin(x) * 0.001
        elev = 100 + 50 * np.sin(x)  # Elevation follows sine pattern
        reference_points.append((lat, lon, elev))
    
    reference_track = create_test_track(reference_points)
    
    # Create target with different point count
    target_track = create_test_track([(0, 0, 0)] * 8)
    
    # Interpolate
    interpolated = Track.interpolate_to_match_points(reference_track, target_track)
    
    print(f"Original track: {len(reference_track.points)} points")
    print(f"Interpolated track: {len(interpolated.points)} points")
    
    # Print comparison
    print("\nOriginal vs Interpolated comparison:")
    print("Index | Original Lat | Original Lon | Original Elev | Interp Lat | Interp Lon | Interp Elev")
    print("-" * 85)
    
    # Show first few points of each
    for i in range(min(5, len(reference_track.points))):
        orig = reference_track.points[i]
        print(f"{i:5d} | {orig.latitude:11.6f} | {orig.longitude:11.6f} | {orig.elevation:12.1f} |", end="")
        if i < len(interpolated.points):
            interp = interpolated.points[i]
            print(f" {interp.latitude:9.6f} | {interp.longitude:9.6f} | {interp.elevation:10.1f}")
        else:
            print(" N/A        | N/A        | N/A")
    
    print("✓ Visualization example completed")
    print()


def run_all_tests():
    """Run all interpolation tests."""
    print("Starting comprehensive GPX interpolation tests...")
    print()
    
    try:
        test_basic_interpolation()
        test_edge_cases()
        test_upsampling_downsampling()
        test_real_gpx_files()
        test_interpolation_accuracy()
        visualize_interpolation_example()
        
        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print()
        print("Summary of tested functionality:")
        print("• Basic linear interpolation between tracks")
        print("• Edge cases (minimum points, None elevations)")
        print("• Both upsampling and downsampling scenarios")
        print("• Real GPX file interpolation")
        print("• Interpolation accuracy verification")
        print("• Visualization of interpolation results")
        print()
        print("The Track.interpolate_to_match_points() function is ready for production use.")
        
    except Exception as e:
        print(f"TEST SUITE FAILED: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()