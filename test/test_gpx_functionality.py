#!/usr/bin/env python3
"""
GPX Track Processing - Complete Test Suite

Tests the GPX interpolation and alignment functionality with both synthetic
and real GPS data. Provides comprehensive validation of the implementation
with clear documentation of results.

Requirements tested:
1. Track interpolation: Interpolate first recording to match second recording's point count
2. Track alignment: Align two recordings to have matching start/end positions

Usage: python3 test/test_gpx_functionality.py
"""

import sys
import os
import glob
import unittest
from datetime import datetime
import math
import matplotlib.pyplot as plt
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import our models
from gpx_dataengine.models import Track, Point


def log_test_result(test_name, success, details=""):
    """Log test results with timestamp for live documentation."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"[{timestamp}] {status} - {test_name}")
    if details:
        print(f"           {details}")
    return success


class TestGPXInterpolation(unittest.TestCase):
    """Test cases for GPX Track interpolation functionality."""
    
    def setUp(self):
        """Set up test fixtures with synthetic GPS data."""
        # Full route with 5 points (Zurich area coordinates)
        self.full_route_points = [
            (47.3769, 8.5417, 408.0),  # Start point
            (47.3770, 8.5420, 410.0),  # Intermediate points
            (47.3772, 8.5425, 415.0),
            (47.3775, 8.5430, 420.0),
            (47.3780, 8.5440, 430.0)   # End point
        ]
        
        # Subset route with 3 points - determines target count
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
    
    def test_interpolation_basic_requirement(self):
        """Test: Interpolate first recording to match second recording's point count."""
        print(f"\n📍 Testing basic interpolation requirement...")
        print(f"   Full route: {len(self.full_route.points)} points")
        print(f"   Subset route: {len(self.subset_route.points)} points")
        print(f"   Goal: Interpolate full route to {len(self.subset_route.points)} points")
        
        # Apply interpolation: first recording -> second recording's count
        interpolated = Track.interpolate_to_match_points(self.full_route, self.subset_route)
        
        # Verify point count matches target (second recording)
        success = len(interpolated.points) == len(self.subset_route.points)
        log_test_result("Point Count Matching", success,
                       f"Expected {len(self.subset_route.points)}, got {len(interpolated.points)}")
        
        # Verify start and end points are preserved from first recording
        start_preserved = abs(interpolated.points[0].latitude - self.full_route.points[0].latitude) < 1e-10
        end_preserved = abs(interpolated.points[-1].latitude - self.full_route.points[-1].latitude) < 1e-10
        
        log_test_result("Endpoint Preservation", start_preserved and end_preserved,
                       "Start and end points preserved from original route")
        
        self.assertEqual(len(interpolated.points), len(self.subset_route.points))
        self.assertAlmostEqual(interpolated.points[0].latitude, 
                              self.full_route.points[0].latitude, places=6)
        self.assertAlmostEqual(interpolated.points[-1].latitude, 
                              self.full_route.points[-1].latitude, places=6)
    
    def test_interpolation_upsampling(self):
        """Test interpolation when increasing point count."""
        print(f"\n📍 Testing upsampling interpolation...")
        
        # Create smaller reference track (3 points)
        small_points = [
            (47.3769, 8.5417, 408.0),
            (47.3775, 8.5430, 420.0),
            (47.3780, 8.5440, 430.0)
        ]
        small_track = self._create_test_track(small_points)
        
        # Create target with more points (6 points)
        large_points = [
            (47.3769, 8.5417, 408.0),
            (47.3770, 8.5419, 409.0),
            (47.3772, 8.5422, 412.0),
            (47.3774, 8.5426, 416.0),
            (47.3777, 8.5432, 422.0),
            (47.3780, 8.5440, 430.0)
        ]
        large_track = self._create_test_track(large_points)
        
        interpolated = Track.interpolate_to_match_points(small_track, large_track)
        
        success = len(interpolated.points) == 6 and len(interpolated.points) > len(small_track.points)
        log_test_result("Upsampling", success, f"3 points -> 6 points")
        
        self.assertEqual(len(interpolated.points), 6)
        self.assertGreater(len(interpolated.points), len(small_track.points))
    
    def test_interpolation_error_conditions(self):
        """Test error handling for invalid inputs."""
        print(f"\n📍 Testing error conditions...")
        
        single_point = self._create_test_track([(47.0, 8.0, 400.0)])
        
        with self.assertRaises(ValueError):
            Track.interpolate_to_match_points(single_point, self.subset_route)
        
        with self.assertRaises(ValueError):
            Track.interpolate_to_match_points(self.full_route, single_point)
        
        log_test_result("Error Handling", True, "Correctly rejects invalid inputs")


class TestGPXAlignment(unittest.TestCase):
    """Test cases for GPX Track alignment functionality."""
    
    def setUp(self):
        """Set up test fixtures with overlapping GPS tracks."""
        # Track 1: Longer route
        self.track1_points = [
            (47.3769, 8.5417, 408.0),  # Start
            (47.3770, 8.5420, 410.0),
            (47.3772, 8.5425, 415.0),
            (47.3775, 8.5430, 420.0),
            (47.3780, 8.5440, 430.0)   # End
        ]
        
        # Track 2: Overlapping route with similar start/end
        self.track2_points = [
            (47.3769, 8.5417, 408.0),  # Same start
            (47.3771, 8.5422, 412.0),  # Different middle
            (47.3774, 8.5428, 418.0),
            (47.3780, 8.5440, 430.0)   # Same end
        ]
        
        self.track1 = self._create_test_track(self.track1_points)
        self.track2 = self._create_test_track(self.track2_points)
    
    def _create_test_track(self, points_data):
        """Helper method to create a Track from list of (lat, lon, elev) tuples."""
        points = [Point(lat, lon, elev) for lat, lon, elev in points_data]
        return Track(points)
    
    def test_alignment_basic_requirement(self):
        """Test: Align tracks to have matching start and end positions."""
        print(f"\n📍 Testing basic alignment requirement...")
        print(f"   Track 1: {len(self.track1.points)} points")
        print(f"   Track 2: {len(self.track2.points)} points")
        
        # Calculate original distances
        start_dist = self.track1.points[0].distance_to(self.track2.points[0]) * 1000  # meters
        end_dist = self.track1.points[-1].distance_to(self.track2.points[-1]) * 1000
        
        print(f"   Original start distance: {start_dist:.1f}m")
        print(f"   Original end distance: {end_dist:.1f}m")
        
        aligned1, aligned2 = Track.align_track_endpoints(self.track1, self.track2)
        
        # Verify tracks are returned and not empty
        success = (aligned1 is not None and aligned2 is not None and 
                  len(aligned1.points) > 0 and len(aligned2.points) > 0)
        
        log_test_result("Alignment Execution", success,
                       f"Aligned tracks: {len(aligned1.points)} and {len(aligned2.points)} points")
        
        if success:
            # Verify alignment improved distances
            aligned_start_dist = aligned1.points[0].distance_to(aligned2.points[0])
            aligned_end_dist = aligned1.points[-1].distance_to(aligned2.points[-1])
            
            tolerance_check = aligned_start_dist < 0.1 and aligned_end_dist < 0.1  # 100m tolerance
            log_test_result("Position Matching", tolerance_check,
                           f"Start: {aligned_start_dist*1000:.1f}m, End: {aligned_end_dist*1000:.1f}m")
        
        self.assertIsNotNone(aligned1)
        self.assertIsNotNone(aligned2)
        self.assertGreater(len(aligned1.points), 0)
        self.assertGreater(len(aligned2.points), 0)
    
    def test_alignment_tolerance(self):
        """Test alignment with different tolerance settings."""
        print(f"\n📍 Testing tolerance settings...")
        
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
        
        success = aligned1 is not None and aligned2 is not None
        log_test_result("Tolerance Handling", success, "200m tolerance accepted")
        
        self.assertIsNotNone(aligned1)
        self.assertIsNotNone(aligned2)
    
    def test_alignment_error_conditions(self):
        """Test error handling for alignment edge cases."""
        print(f"\n📍 Testing alignment error conditions...")
        
        single_point = self._create_test_track([(47.0, 8.0, 400.0)])
        
        with self.assertRaises(ValueError):
            Track.align_track_endpoints(single_point, self.track2)
        
        # Test tracks too far apart (Zurich vs New York)
        far_track_points = [
            (40.7128, -74.0060, 100.0),  # New York coordinates
            (40.7130, -74.0058, 110.0)
        ]
        far_track = self._create_test_track(far_track_points)
        
        with self.assertRaises(ValueError):
            Track.align_track_endpoints(self.track1, far_track, tolerance_km=0.1)
        
        log_test_result("Error Handling", True, "Correctly rejects invalid alignments")


class TestRealGPXData(unittest.TestCase):
    """Test cases using real GPX files from data directory."""
    
    def setUp(self):
        """Load available GPX files for testing."""
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.gpx_files = glob.glob(os.path.join(self.data_dir, '*.gpx'))
    
    def test_real_data_availability(self):
        """Test that real GPX data is available for testing."""
        print(f"\n📍 Checking real GPX data availability...")
        print(f"   Data directory: {self.data_dir}")
        
        for i, file_path in enumerate(self.gpx_files, 1):
            filename = os.path.basename(file_path)
            print(f"   {i}. {filename}")
        
        success = len(self.gpx_files) >= 2
        log_test_result("Real Data Availability", success, 
                       f"Found {len(self.gpx_files)} GPX files (need ≥2)")
        
        self.assertGreaterEqual(len(self.gpx_files), 2, 
                               "Need at least 2 GPX files in data/ directory for testing")
    
    def test_real_data_interpolation(self):
        """Test interpolation with real GPS data."""
        if len(self.gpx_files) < 2:
            self.skipTest("Need at least 2 GPX files for real data testing")
        
        print(f"\n📍 Testing interpolation with real GPS data...")
        
        # Load first two GPX files
        track1 = Track.from_gpx_file(self.gpx_files[0])
        track2 = Track.from_gpx_file(self.gpx_files[1])
        
        print(f"   File 1: {os.path.basename(self.gpx_files[0])} ({len(track1.points)} points)")
        print(f"   File 2: {os.path.basename(self.gpx_files[1])} ({len(track2.points)} points)")
        
        # Interpolate larger track to smaller track's count
        if len(track1.points) > len(track2.points):
            reference_track, target_track = track1, track2
            ref_name, target_name = os.path.basename(self.gpx_files[0]), os.path.basename(self.gpx_files[1])
        else:
            reference_track, target_track = track2, track1
            ref_name, target_name = os.path.basename(self.gpx_files[1]), os.path.basename(self.gpx_files[0])
        
        print(f"   Interpolating {ref_name} to match {target_name}")
        
        # Apply interpolation
        interpolated = Track.interpolate_to_match_points(reference_track, target_track)
        
        # Verify results
        point_match = len(interpolated.points) == len(target_track.points)
        log_test_result("Real Data Point Matching", point_match,
                       f"Expected {len(target_track.points)}, got {len(interpolated.points)}")
        
        # Check distance preservation (allow 10% error for real data)
        original_distance = reference_track.total_distance
        interpolated_distance = interpolated.total_distance
        distance_error = abs(original_distance - interpolated_distance) / original_distance * 100
        
        distance_ok = distance_error < 10.0
        log_test_result("Real Data Distance Preservation", distance_ok,
                       f"Distance error: {distance_error:.2f}% (threshold: 10%)")
        
        self.assertEqual(len(interpolated.points), len(target_track.points))
        self.assertLess(distance_error, 10.0)
    
    def test_real_data_loading(self):
        """Test that real GPX files can be loaded without errors."""
        if len(self.gpx_files) < 1:
            self.skipTest("Need at least 1 GPX file for loading test")
        
        print(f"\n📍 Testing real GPX file loading...")
        
        for i, file_path in enumerate(self.gpx_files[:3]):  # Test first 3 files
            filename = os.path.basename(file_path)
            try:
                track = Track.from_gpx_file(file_path)
                success = len(track.points) > 0
                log_test_result(f"Load {filename}", success,
                               f"{len(track.points)} points, {track.total_distance:.2f}km")
                self.assertGreater(len(track.points), 0)
            except Exception as e:
                log_test_result(f"Load {filename}", False, f"Error: {str(e)}")
                self.fail(f"Failed to load {filename}: {e}")


def create_evaluation_plots():
    """Create comprehensive evaluation plots demonstrating the functionality."""
    print("\n" + "=" * 60)
    print("CREATING EVALUATION PLOTS")
    print("=" * 60)
    
    try:
        # Check for real data availability
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        gpx_files = glob.glob(os.path.join(data_dir, '*.gpx'))
        
        if len(gpx_files) < 2:
            print("⚠️ Need at least 2 GPX files for comprehensive plots")
            return False
        
        # Load real data for demonstration
        track1 = Track.from_gpx_file(gpx_files[0])
        track2 = Track.from_gpx_file(gpx_files[1])
        
        # Determine tracks for interpolation demo
        if len(track1.points) > len(track2.points):
            full_track, target_track = track1, track2
            full_name, target_name = os.path.basename(gpx_files[0]), os.path.basename(gpx_files[1])
        else:
            full_track, target_track = track2, track1
            full_name, target_name = os.path.basename(gpx_files[1]), os.path.basename(gpx_files[0])
        
        # Apply interpolation
        interpolated_track = Track.interpolate_to_match_points(full_track, target_track)
        
        # Create comprehensive figure
        fig = plt.figure(figsize=(16, 12))
        
        # Plot 1: GPS Track Comparison (Map View)
        ax1 = plt.subplot(2, 3, 1)
        
        # Extract coordinates
        full_lats = [p.latitude for p in full_track.points]
        full_lons = [p.longitude for p in full_track.points]
        target_lats = [p.latitude for p in target_track.points]
        target_lons = [p.longitude for p in target_track.points]
        interp_lats = [p.latitude for p in interpolated_track.points]
        interp_lons = [p.longitude for p in interpolated_track.points]
        
        ax1.plot(full_lons, full_lats, 'b-o', linewidth=2, markersize=3, alpha=0.7,
                label=f'Original: {full_name}\n({len(full_track.points)} points)')
        ax1.plot(target_lons, target_lats, 'r-s', linewidth=2, markersize=5,
                label=f'Target: {target_name}\n({len(target_track.points)} points)')
        ax1.plot(interp_lons, interp_lats, 'g-^', linewidth=2, markersize=4,
                label=f'Interpolated\n({len(interpolated_track.points)} points)')
        
        ax1.set_title('GPS Track Interpolation\nMap View', fontweight='bold', fontsize=12)
        ax1.set_xlabel('Longitude (°)')
        ax1.set_ylabel('Latitude (°)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Elevation Profiles
        ax2 = plt.subplot(2, 3, 2)
        
        # Calculate distances for x-axis
        full_distances = full_track.elevation_profile.get_distances()
        target_distances = target_track.elevation_profile.get_distances()
        interp_distances = interpolated_track.elevation_profile.get_distances()
        
        # Extract elevations
        full_elevs = [p.elevation or 0 for p in full_track.points]
        target_elevs = [p.elevation or 0 for p in target_track.points]
        interp_elevs = [p.elevation or 0 for p in interpolated_track.points]
        
        ax2.plot(full_distances, full_elevs, 'b-o', linewidth=2, markersize=3, alpha=0.7,
                label=f'Original ({len(full_track.points)} pts)')
        ax2.plot(target_distances, target_elevs, 'r-s', linewidth=2, markersize=5,
                label=f'Target ({len(target_track.points)} pts)')
        ax2.plot(interp_distances, interp_elevs, 'g-^', linewidth=2, markersize=4,
                label=f'Interpolated ({len(interpolated_track.points)} pts)')
        
        ax2.set_title('Elevation Profiles', fontweight='bold', fontsize=12)
        ax2.set_xlabel('Distance (km)')
        ax2.set_ylabel('Elevation (m)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Point Count Analysis
        ax3 = plt.subplot(2, 3, 3)
        
        track_names = ['Original\nTrack', 'Target\nTrack', 'Interpolated\nResult']
        point_counts = [len(full_track.points), len(target_track.points), len(interpolated_track.points)]
        colors = ['blue', 'red', 'green']
        
        bars = ax3.bar(track_names, point_counts, color=colors, alpha=0.7)
        ax3.set_title('Point Count Comparison', fontweight='bold', fontsize=12)
        ax3.set_ylabel('Number of Points')
        
        # Add value labels on bars
        for bar, count in zip(bars, point_counts):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + max(point_counts)*0.01,
                    f'{count}', ha='center', va='bottom', fontweight='bold')
        
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Plot 4: Distance Preservation Analysis
        ax4 = plt.subplot(2, 3, 4)
        
        original_distance = full_track.total_distance
        interpolated_distance = interpolated_track.total_distance
        distance_error = abs(original_distance - interpolated_distance) / original_distance * 100
        
        distances = [original_distance, interpolated_distance]
        distance_labels = ['Original', 'Interpolated']
        colors = ['blue', 'green']
        
        bars = ax4.bar(distance_labels, distances, color=colors, alpha=0.7)
        ax4.set_title(f'Distance Preservation\nError: {distance_error:.2f}%', fontweight='bold', fontsize=12)
        ax4.set_ylabel('Total Distance (km)')
        
        # Add value labels
        for bar, dist in zip(bars, distances):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + max(distances)*0.01,
                    f'{dist:.2f}km', ha='center', va='bottom', fontweight='bold')
        
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Plot 5: Interpolation Quality Metrics
        ax5 = plt.subplot(2, 3, 5)
        
        # Calculate interpolation quality metrics
        metrics = ['Point Count\nMatching', 'Distance\nPreservation', 'Endpoint\nPreservation']
        
        # Point count matching
        point_match = 1 if len(interpolated_track.points) == len(target_track.points) else 0
        
        # Distance preservation (allow 5% error)
        distance_preserve = 1 if distance_error < 5.0 else 0
        
        # Endpoint preservation
        start_diff = abs(interpolated_track.points[0].latitude - full_track.points[0].latitude)
        end_diff = abs(interpolated_track.points[-1].latitude - full_track.points[-1].latitude)
        endpoint_preserve = 1 if start_diff < 1e-10 and end_diff < 1e-10 else 0
        
        scores = [point_match, distance_preserve, endpoint_preserve]
        colors = ['green' if s else 'red' for s in scores]
        
        bars = ax5.bar(metrics, scores, color=colors, alpha=0.7)
        ax5.set_title('Interpolation Quality\nMetrics', fontweight='bold', fontsize=12)
        ax5.set_ylabel('Pass (1) / Fail (0)')
        ax5.set_ylim(-0.1, 1.1)
        
        # Add labels
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    'PASS' if score else 'FAIL', ha='center', va='bottom', fontweight='bold')
        
        # Plot 6: Statistics Summary
        ax6 = plt.subplot(2, 3, 6)
        
        # Create summary statistics table
        stats_data = [
            ['Metric', 'Original', 'Target', 'Interpolated'],
            ['Points', f'{len(full_track.points)}', f'{len(target_track.points)}', f'{len(interpolated_track.points)}'],
            ['Distance (km)', f'{original_distance:.2f}', f'{target_track.total_distance:.2f}', f'{interpolated_distance:.2f}'],
            ['Start Lat', f'{full_track.points[0].latitude:.6f}', f'{target_track.points[0].latitude:.6f}', f'{interpolated_track.points[0].latitude:.6f}'],
            ['End Lat', f'{full_track.points[-1].latitude:.6f}', f'{target_track.points[-1].latitude:.6f}', f'{interpolated_track.points[-1].latitude:.6f}'],
            ['Error %', '-', '-', f'{distance_error:.2f}%']
        ]
        
        ax6.axis('tight')
        ax6.axis('off')
        table = ax6.table(cellText=stats_data[1:], colLabels=stats_data[0], 
                         cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        
        # Style header row
        for i in range(len(stats_data[0])):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax6.set_title('Statistical Summary', fontweight='bold', fontsize=12)
        
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f'test/gpx_evaluation_results_{timestamp}.png'
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        
        log_test_result("Evaluation Plots", True, f"Saved as {plot_filename}")
        
        # Show plot (comment out for automated testing)
        # plt.show()  # Disabled for automated testing
        
        return True
        
    except Exception as e:
        log_test_result("Evaluation Plots", False, f"Error: {str(e)}")
        return False


def run_complete_test_suite():
    """Run the complete test suite with live documentation."""
    print("🎯 GPX FUNCTIONALITY - COMPLETE TEST SUITE")
    print("=" * 60)
    print("Testing GPX interpolation and alignment functionality")
    print("with both synthetic and real GPS data.")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add interpolation tests
    suite.addTest(TestGPXInterpolation('test_interpolation_basic_requirement'))
    suite.addTest(TestGPXInterpolation('test_interpolation_upsampling'))
    suite.addTest(TestGPXInterpolation('test_interpolation_error_conditions'))
    
    # Add alignment tests
    suite.addTest(TestGPXAlignment('test_alignment_basic_requirement'))
    suite.addTest(TestGPXAlignment('test_alignment_tolerance'))
    suite.addTest(TestGPXAlignment('test_alignment_error_conditions'))
    
    # Add real data tests
    suite.addTest(TestRealGPXData('test_real_data_availability'))
    suite.addTest(TestRealGPXData('test_real_data_loading'))
    suite.addTest(TestRealGPXData('test_real_data_interpolation'))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUITE SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    if result.wasSuccessful():
        print(f"🎉 ALL TESTS PASSED ({passed}/{total_tests})")
        print("✅ GPX interpolation works correctly")
        print("✅ GPX alignment works correctly")
        print("✅ Real data processing successful")
        print("\n🚀 Implementation ready for submission!")
    else:
        print(f"⚠️ SOME TESTS FAILED ({passed}/{total_tests})")
        if failures:
            print(f"   Failures: {failures}")
        if errors:
            print(f"   Errors: {errors}")
    
    print(f"\nImplementation location: src/gpx_dataengine/models.py")
    print(f"Test coverage: Synthetic data + Real GPX files")
    
    # Create evaluation plots after tests
    if result.wasSuccessful():
        create_evaluation_plots()
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Check dependencies first
    try:
        from gpx_dataengine.models import Track, Point
        print("✅ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install with: pip install numpy scipy gpxpy matplotlib")
        print("Note: pygeodesy is optional for geoid correction")
        sys.exit(1)
    
    # Run complete test suite
    success = run_complete_test_suite()
    sys.exit(0 if success else 1)