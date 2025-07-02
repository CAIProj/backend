### Class Diagram for `plotter.py`: `Plotter` and `SynchronizedElevationPlotter` classes

```mermaid
classDiagram

    class Plotter {
        -profiles: dict~str, ElevationProfile~
        +__init__(profiles: Optional~List[Union[ElevationProfile, Tuple[ElevationProfile, str]]]~)
        +add_profiles(*profiles): void
        +set_profiles(profiles_dict: dict~str, ElevationProfile~): void
        +plot_distance_vs_elevation(title: str, xlabel: str, ylabel: str, output: Optional~str~): void
        +plot_lat_vs_lon(title: str, xlabel: str, ylabel: str, output: Optional~str~): void
        +plot_3d_lat_lon_elevation(title: str, xlabel: str, ylabel: str, zlabel: str, output: Optional~str~): void
    }

    class SynchronizedElevationPlotter {
        +plot_comparison(profile1: ElevationProfile, profile2: ElevationProfile, ...): void
        +get_tolerance_vector(profile1: ElevationProfile, profile2: ElevationProfile, tolerance: float): ToleranceVector
        +kdtree_tolerance(profile1: ElevationProfile, profile2: ElevationProfile, tolerance: float): ToleranceVector
        +elevation_sync(gpx1: list~Point~, gpx2: list~Point~, ...): SyncResult
        +start_sync(gpx1: list~Point~, gpx2: list~Point~, ...): SyncResult
        +interpolate_elevations(gpx1: list~Point~, gpx2: list~Point~, ...): SyncResult
    }

    Plotter --> ElevationProfile : uses
    SynchronizedElevationPlotter --> ElevationProfile : uses
    SynchronizedElevationPlotter --> Point : uses
```

#### Type Aliases

- `ToleranceVector`: Boolean NumPy array (`np.ndarray[bool]`)
- `SyncResult`: Tuple of (ElevationProfile, ElevationProfile, ToleranceVector)
