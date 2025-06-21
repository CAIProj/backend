from plotter import plot2d, plot3d, plot_surface
import argparse

def main():
    parser = argparse.ArgumentParser(description="Compare GPX Elevation with API")
    parser.add_argument("plot_type", choices=["3d", "elevation", "surface"])
    parser.add_argument("base_gpx", help='Path to primary GPX file')
    parser.add_argument("--gpx2", help='Path to a comparison GPX file')

    #Elevation specific parameters
    elevation_group = parser.add_argument_group("Elevation Plot Options")
    elevation_group.add_argument("--sync-method",
                                 choices=["elevation_sync", "start_sync", "interpolate_elevations"],
                                 default="elevation_sync",
                                 help="Synchronisation Method (default: elevation_sync")
    elevation_group.add_argument("--use-api", action="store_true", help="Use API instead of comparison file")
    elevation_group.add_argument("--tolerance", type=float, help="Enable display of specified distance tolerance (km)")
    elevation_group.add_argument("--tolerance-method", choices=["standard", "kdtree"], default="standard",
                                 help="Tolerance calculation method")

    #General optional parameters
    general_group = parser.add_argument_group("General Options")
    general_group.add_argument("--output", help="Save plot to file instead of displaying")
    general_group.add_argument("--title", help="Custom title for plot")

    args = parser.parse_args()

    #validation
    if args.plot_type == "elevation":
        if not (args.gpx2 or args.use_api):
            parser.error("2D plots require --gpx2 OR --use-api")
        if args.tolerance and not args.gpx2 and not args.use_api:
            parser.error("Tolerance requires a source of comparison")
    if args.plot_type == "3d" and not args.gpx2:
        parser.error("3D plots require --gpx2")
    if args.tolerance and not args.tolerance_method:
        parser.error("--tolerance-method required when using tolerance")

    #call corresponding functions in plotter.py
    if args.plot_type == "3d":
        plot3d(args)
    elif args.plot_type == "elevation":
        plot2d(args)
    elif args.plot_type == "surface":
        plot_surface(args)


if __name__ == "__main__":
    main()

