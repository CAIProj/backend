from src.plotter import Plotter, plot_synchronized_2d, plot_surface
from src.models import Track
import argparse

def main():
    parser = argparse.ArgumentParser(description="Compare GPX Elevation with API")
    parser.add_argument("plot_type", choices=["3d", "elevation", "surface"])
    parser.add_argument("base_gpx", help="Path to the base GPX file")
    parser.add_argument("--gpx2", help="Path to a comparison GPX file")

    # Elevation specific options
    elevation_group = parser.add_argument_group("Elevation Plot Options")
    elevation_group.add_argument(
        "--sync-method",
        choices=["elevation_sync", "start_sync", "interpolate_elevations"],
        default="elevation_sync",
        help="Synchronisation Method (default: elevation_sync)"
    )
    elevation_group.add_argument("--use-api", action="store_true", help="Use elevation from API instead of a second GPX file")
    elevation_group.add_argument("--tolerance", type=float, help="Tolerance range in km for comparison")
    elevation_group.add_argument(
        "--tolerance-method",
        choices=["standard", "kdtree"],
        default="standard",
        help="Method for calculating tolerance (default: standard)"
    )

    # General options
    general_group = parser.add_argument_group("General Options")
    general_group.add_argument("--output", help="Save the plot to this file instead of displaying it")
    general_group.add_argument("--title", help="Custom title for the plot")

    args = parser.parse_args()

    # Argument Validation 
    if args.plot_type == "elevation":
        if not (args.gpx2 or args.use_api):
            parser.error("Elevation plots require --gpx2 or --use-api")
        if args.tolerance and not args.gpx2 and not args.use_api:
            parser.error("Tolerance requires a comparison source: either a second file using --gpx2 or elevation data using --use-api")

    if args.plot_type == "3d" and not args.gpx2:
        parser.error("3D plots require --gpx2")

    if args.tolerance and not args.tolerance_method:
        parser.error("--tolerance-method is required when using tolerance")

    # Plotting logic
    if args.plot_type == "3d":
        output = args.output if args.output else None # file path to save the plot, if None display the plot plot
        try:
            profile1 = Track.from_gpx_file(args.base_gpx).elevation_profile
            profile2 = Track.from_gpx_file(args.gpx2).elevation_profile

            plotter = Plotter([
                profile1,
                profile2,
            ])

            if args.title:
                plotter.plot_3d_lat_lon_elevation(title=args.title, output=output)
            else:
                plotter.plot_3d_lat_lon_elevation(output=output)

        except Exception as e:
            raise RuntimeError(f"3D plot failed: {e}")

    elif args.plot_type == "elevation":
        plot_synchronized_2d(args)

    elif args.plot_type == "surface":
        plot_surface(args)

if __name__ == "__main__":
    main()
