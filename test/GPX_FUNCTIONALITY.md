# GPX Track Interpolation and Alignment

This module provides functionality for comparing GPX recordings by interpolating and aligning tracks.

## Overview

When comparing two GPX recordings of the same route, they often have different numbers of points or different start/end positions. This module provides two key functions to enable direct comparison:

1. **Interpolation**: Adjust point count to match between tracks
2. **Alignment**: Align start and end positions between tracks

## Core Functions

### `Track.interpolate_to_match_points(full_route, subset_route)`

Interpolates the first recording to match the second recording's point count.

**Purpose**: When you have a detailed GPS recording and a simplified version (subset), interpolate the detailed version to have the same number of points for direct comparison.

**Parameters**:
- `full_route` (Track): The complete route recording to be interpolated
- `subset_route` (Track): The subset recording that determines target point count

**Returns**: 
- Track: New Track instance with interpolated points matching subset count

**Example**:
```python
from gpx_dataengine.models import Track

# Load recordings
full_route = Track.from_gpx_file('detailed_hike.gpx')      # 100 points
subset = Track.from_gpx_file('key_waypoints.gpx')          # 5 points

# Interpolate full route to match subset
interpolated = Track.interpolate_to_match_points(full_route, subset)

# Result: interpolated now has 5 points for direct comparison with subset
```

### `Track.align_track_endpoints(track1, track2, tolerance_km=0.1)`

Aligns two tracks by truncating them to have matching start and end positions.

**Purpose**: When recordings of the same route were started or stopped at different points, find the common segment for comparison.

**Parameters**:
- `track1` (Track): First GPX track to align
- `track2` (Track): Second GPX track to align
- `tolerance_km` (float): Maximum distance to consider points as matching (default: 100m)

**Returns**:
- tuple[Track, Track]: Aligned versions of both tracks

**Example**:
```python
# Load recordings that started/ended at different points
recording1 = Track.from_gpx_file('started_early.gpx')
recording2 = Track.from_gpx_file('ended_late.gpx')

# Align endpoints
aligned1, aligned2 = Track.align_track_endpoints(recording1, recording2)

# Result: both tracks now start and end at approximately the same positions
```

## Complete Workflow

For comprehensive comparison of two GPX recordings:

```python
from gpx_dataengine.models import Track

# 1. Load recordings
track1 = Track.from_gpx_file('recording1.gpx')
track2 = Track.from_gpx_file('recording2.gpx') 

# 2. Align endpoints (if needed)
aligned1, aligned2 = Track.align_track_endpoints(track1, track2)

# 3. Interpolate to matching point counts
if len(aligned1.points) != len(aligned2.points):
    if len(aligned1.points) > len(aligned2.points):
        final1 = Track.interpolate_to_match_points(aligned1, aligned2)
        final2 = aligned2
    else:
        final1 = aligned1  
        final2 = Track.interpolate_to_match_points(aligned2, aligned1)
else:
    final1, final2 = aligned1, aligned2

# 4. Direct point-by-point comparison now possible
for i in range(len(final1.points)):
    p1 = final1.points[i]
    p2 = final2.points[i]
    distance_diff = p1.distance_to(p2) * 1000  # meters
    elevation_diff = abs(p1.elevation - p2.elevation)
    print(f"Point {i}: {distance_diff:.1f}m apart, {elevation_diff:.1f}m elevation diff")
```

## Key Features

### Interpolation
- **Distance-based**: Uses cumulative distances along route for accurate interpolation
- **Preserves endpoints**: Start and end points are exactly maintained
- **Linear interpolation**: Uses scipy.interpolate.interp1d for smooth transitions
- **Handles elevations**: Interpolates latitude, longitude, and elevation values
- **Error handling**: Validates input and provides clear error messages

### Alignment  
- **Tolerance-based**: Configurable distance tolerance for matching points
- **Efficient search**: Searches only first/last 20% of tracks for performance
- **Bidirectional**: Finds best matches for both start and end points
- **Preserves data**: Returns truncated tracks without modifying originals
- **Robust**: Handles various GPS recording patterns

## Testing

Run the comprehensive test suite to verify functionality:

```bash
python3 test/test_gpx_functionality.py
```

The test suite includes:
- Unit tests with synthetic GPS data
- Integration tests with real GPX files  
- Error condition validation
- Live documentation of test results
- Comprehensive evaluation plots showing results

Place GPX files in the `data/` directory for real-world testing.

**Generated Plots:**
After successful test completion, comprehensive evaluation plots are automatically generated showing:
- GPS track comparison (map view)
- Elevation profile analysis
- Point count comparison
- Distance preservation metrics
- Quality assessment scores
- Statistical summary table

Plots are saved as `test/gpx_evaluation_results_YYYYMMDD_HHMMSS.png`

## Dependencies

- numpy: For numerical operations and linear spacing
- scipy: For interpolation functions
- pygeodesy: For geoid calculations and coordinate handling
- gpxpy: For GPX file parsing
- matplotlib: For evaluation plots and visualization

Install with:
```bash
pip install numpy scipy pygeodesy gpxpy matplotlib
```