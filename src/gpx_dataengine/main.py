from plotter import plot3d, Plotter
from models import Track

#TODO: Improve parser to handle more options and arguments


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare GPX Elevation with API")
    parser.add_argument("gpx1", help='Path to the GPX file')
    parser.add_argument("--gpx2", help='Path to a second GPX file')
    parser.add_argument("--mode", default="2d", choices=["2d","3d"],help="What kind of plot?")

    args = parser.parse_args()

    if not args.gpx2:
        print("Simple plot functionality not yet added")
    else:
        if args.mode == "2d":
            gpx_file_1 = args.gpx1
            gpx_file_2 = args.gpx2

            try:
                track_1 = Track.from_gpx_file(gpx_file_1)
                track_2 = Track.from_gpx_file(gpx_file_2)

                # truncate longer file
                min_len = min(len(track_1.points), len(track_2.points))
                track_1.points = track_1.points[:min_len]
                track_2.points = track_2.points[:min_len]

                plotter = Plotter([
                    track_1.elevation_profile,
                    track_2.elevation_profile 
                ])
                plotter.plot_distance_vs_elevation()
            except:
                raise
        elif args.mode == "3d":
            plot3d(args)
        else:
            print("Invalid options")


