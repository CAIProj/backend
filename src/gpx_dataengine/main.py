from plotter import plot2d, plot3d

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
            plot2d(args)
        elif args.mode == "3d":
            plot3d(args)
        else:
            print("Invalid options")


