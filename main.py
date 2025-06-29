from src.plotter import Plotter, plot_synchronized_2d
from src.models import Track
from src.elevation_api import OpenStreetMapElevationAPI, OpenElevationAPI
import argparse

def main():
    parser = argparse.ArgumentParser(description="Compare GPX Elevation Profiles")

    parser.add_argument(
        "plot_type",
        choices=["3d", "elevation", "surface"],
        help="Plot type: '3d' for basic 3D plot, 'elevation' for optional sync comparison, 'surface' for elevation surface plot"
    )
    parser.add_argument("base_gpx", help="Path to the base GPX file")

    # Comparison source options
    parser.add_argument("--second-gpx", help="Add a second GPX file")
    parser.add_argument("--add-openstreetmap", action="store_true", help="Add elevation data of base GPX using OpenStreetMapElevationAPI")
    parser.add_argument("--add-openelevation", action="store_true", help="Add elevation data of base GPX using OpenElevationAPI")
    parser.add_argument("--add-loess1", action="store_true", help="Add smoothed base GPX elevations with LOESS v1")
    parser.add_argument("--add-loess2", action="store_true", help="Add smoothed base GPX elevations with LOESS v2")
    parser.add_argument("--add-spline", action="store_true", help="Add smoothed base GPX elevations with spline")
    

    # Synchronized elevation options
    synchronized_elevation_group = parser.add_argument_group("Synchronized Elevation Plot Options")
    synchronized_elevation_group.add_argument(
        "--sync-method",
        choices=["elevation_sync", "start_sync", "interpolate_elevations"],
        help="Synchronisation method to align elevation profiles"
    )
    synchronized_elevation_group.add_argument("--tolerance", type=float, help="Tolerance range in km for comparison")
    synchronized_elevation_group.add_argument(
        "--tolerance-method",
        choices=["standard", "kdtree"],
        help="Method for calculating tolerance"
    )

    # General options
    general_group = parser.add_argument_group("General Options")
    general_group.add_argument("--output", help="Save the plot to this file instead of displaying it")
    general_group.add_argument("--title", help="Custom title for the plot")



    # Parse arguments
    args = parser.parse_args()

    # Validate sync-related inputs
    # --- For synchronized elevation plots exactly one comparison source must be specified
    if args.plot_type == "elevation" and args.sync_method:  
        sync_sources = [
            args.second_gpx,
            args.add_openstreetmap,
            args.add_openelevation,
            args.add_loess1,
            args.add_loess2,
            args.add_spline
        ]
        num_sources = sum(bool(src) for src in sync_sources)
        
        if num_sources != 1:
            parser.error("When using --sync-method, exactly one comparison source must be specified: "
                         "--second-gpx or one of the --add-* options")
    # --- tolerance and tolerance_method are only relevant for synchronized elevation plots
    if args.tolerance or args.tolerance_method:
        if not args.plot_type == "elevation":
            if args.sync_method:
                parser.error("For synced plot plot-type must be `elevation`")
            else:
                parser.error("For synced plot plot-type must be `elevation` and --sync-method must be specified")
        else:
            if not args.sync_method:
                parser.error("For synced plot --sync-method is required")
        

    # Load base track and other tracks according to plot type
    base_gpx_track = Track.from_gpx_file(args.base_gpx)
    loaded_tracks = {"base_gpx": base_gpx_track}

    if args.plot_type == "elevation" and args.sync_method:
        if args.second_gpx:
            loaded_tracks["second_gpx"] = Track.from_gpx_file(args.second_gpx)
        elif args.add_openstreetmap:
            loaded_tracks["openstreetmap"] = base_gpx_track.with_api_elevations(OpenStreetMapElevationAPI)
        elif args.add_openelevation:
            loaded_tracks["openelevation"] = base_gpx_track.with_api_elevations(OpenElevationAPI)
        elif args.add_loess1:
            loaded_tracks["loess1"] = base_gpx_track.with_smoothed_elevations("loess_v1")
        elif args.add_loess2:
            loaded_tracks["loess2"] = base_gpx_track.with_smoothed_elevations("loess_v2")
        elif args.add_spline:
            loaded_tracks["spline"] = base_gpx_track.with_smoothed_elevations("spline")
    else:
        # Load all tracks based one the given arguments
        if args.second_gpx:
            loaded_tracks["second_gpx"] = Track.from_gpx_file(args.second_gpx)
        if args.add_openstreetmap:
            loaded_tracks["openstreetmap"] = base_gpx_track.with_api_elevations(OpenStreetMapElevationAPI)
        if args.add_openelevation:
            loaded_tracks["openelevation"] = base_gpx_track.with_api_elevations(OpenElevationAPI)
        if args.add_loess1:
            loaded_tracks["loess1"] = base_gpx_track.with_smoothed_elevations("loess_v1")
        if args.add_loess2:
            loaded_tracks["loess2"] = base_gpx_track.with_smoothed_elevations("loess_v2")
        if args.add_spline:
            loaded_tracks["spline"] = base_gpx_track.with_smoothed_elevations("spline")


    # Plotting logic
    if args.plot_type == "3d":
        try:
            plotter = Plotter()
            
            # Add all the profiles from loaded tracks
            for name, track in loaded_tracks.items():
                plotter.add_profiles((track.elevation_profile, name.replace('_', ' ').capitalize()))
            if args.title:
                plotter.plot_3d_lat_lon_elevation(title=args.title, output=args.output)
            else:
                plotter.plot_3d_lat_lon_elevation(output=args.output)
        except Exception as e:
            raise RuntimeError(f"Failed to plot 3d: {e}")

    elif args.plot_type == "elevation":
        if args.sync_method:
            plot_synchronized_2d(args)
        else:
            try:
                plotter = Plotter()

                # Add all the profiles from loaded tracks
                for name, track in loaded_tracks.items():
                    plotter.add_profiles((track.elevation_profile, name.replace('_', ' ').capitalize()))
                    
                # Plot ele vs. distance
                if args.title:
                    plotter.plot_distance_vs_elevation(title=args.title, output=args.output)
                else:
                    plotter.plot_distance_vs_elevation(output=args.output)
            except Exception as e:
                raise RuntimeError(f"Failed to plot elevation: {e}")

    elif args.plot_type == "surface":
        try:
            plotter = Plotter()
            for name, track in loaded_tracks.items():
                plotter.add_profiles((track.elevation_profile, name.replace('_', ' ').capitalize()))
            if args.title:
                plotter.plot_lat_vs_lon(title=args.title, output=args.output)
            else:
                plotter.plot_lat_vs_lon(output=args.output)
        except Exception as e:
            raise RuntimeError(f"Failed to plot elevation: {e}")

if __name__ == "__main__":
    main()
