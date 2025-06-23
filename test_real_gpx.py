#!/usr/bin/env python3
"""
Test GPX interpolation with real GPX files from the data directory.

This script demonstrates the interpolation functionality using actual GPX files.
Run this after installing dependencies: pip install numpy scipy pygeodesy gpxpy
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from gpx_dataengine.models import Track, Point
    
    def test_with_real_gpx_files():
        """Test interpolation with real GPX files."""
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # List available GPX files
        gpx_files = [f for f in os.listdir(data_dir) if f.endswith('.gpx')]
        
        if len(gpx_files) < 2:
            print("Need at least 2 GPX files in data/ directory")
            return
        
        print("Available GPX files:")
        for i, file in enumerate(gpx_files):
            print(f"  {i}: {file}")
        
        # Load two different GPX files
        file1 = os.path.join(data_dir, gpx_files[0])
        file2 = os.path.join(data_dir, gpx_files[1])
        
        print(f"\nLoading {gpx_files[0]}...")
        track1 = Track.from_gpx_file(file1)
        
        print(f"Loading {gpx_files[1]}...")
        track2 = Track.from_gpx_file(file2)
        
        print(f"\nBEFORE INTERPOLATION:")
        print(f"Track 1: {len(track1.points)} points, {track1.total_distance:.3f} km")
        print(f"Track 2: {len(track2.points)} points, {track2.total_distance:.3f} km")
        
        # Test interpolation: interpolate track1 to match track2's point count
        print(f"\nApplying interpolation...")
        print(f"interpolate_to_match_points(track1, track2)")
        
        interpolated = Track.interpolate_to_match_points(track1, track2)
        
        print(f"\nAFTER INTERPOLATION:")
        print(f"Original track 1: {len(track1.points)} points")
        print(f"Track 2 (target): {len(track2.points)} points")
        print(f"Interpolated track 1: {len(interpolated.points)} points")
        print(f"Interpolated distance: {interpolated.total_distance:.3f} km")
        
        # Verify
        assert len(interpolated.points) == len(track2.points), "Point counts should match"
        
        print(f"\n✓ SUCCESS: Track 1 interpolated to match Track 2's point count!")
        print(f"✓ Both tracks now have {len(track2.points)} points for comparison")
        
        return True
    
    if __name__ == '__main__':
        print("Testing GPX Interpolation with Real Files")
        print("=" * 50)
        test_with_real_gpx_files()
        
except ImportError as e:
    print("Dependencies not available:")
    print(f"Error: {e}")
    print("\nTo install dependencies:")
    print("pip install numpy scipy pygeodesy gpxpy matplotlib")
    print("\nAlternatively, run the logic tests:")
    print("python3 test/test_gpx_logic_unittest.py")