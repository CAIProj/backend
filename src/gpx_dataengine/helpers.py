import os
from matplotlib import pyplot as plt
import gpxpy
import gpxpy.gpx

def get_elevation_parameters(segment: gpxpy.gpx.GPXTrackSegment):
    ascend = 0
    descend = 0
    greatest_ascend = 0
    greatest_descend = 0
    points = segment.points

    for i in range(len(points) - 1):
        elevation_interval = points[i + 1].elevation - points[i].elevation
        if elevation_interval > 0:
            ascend += elevation_interval
            if elevation_interval > greatest_ascend:
                greatest_ascend = elevation_interval
        else:
            descend += abs(elevation_interval)
            if abs(elevation_interval) > greatest_descend:
                greatest_descend = abs(elevation_interval)

    return ascend, descend, greatest_ascend, greatest_descend


def plot(segment: gpxpy.gpx.GPXTrackSegment, name: str):
    dist_points = get_distance_points(segment)
    elev_points = [p.elevation for p in segment.points]

    plt.plot(dist_points, elev_points, label=name)

    plt.xlabel("Distance [m]")
    plt.ylabel("Elevation [m]")


def plot_file(file_name: str, name: str):
    gpx = open_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name))
    for track in gpx.tracks:
        for segment in track.segments:
            # Optional
            print(total_time(segment))
            print(get_elevation_parameters(segment))

            plot(segment, name)


plot_file("2024-10-17_13_02_around_thi.gpx", "Around THI")
plot_file("2024-10-24_12_42_hohe_mandel.gpx", "Hohe Mandel.gpx")
plot_file("31_Mar_2025_10_30_57.gpx", "Tom's Data")

plt.legend(loc = "lower right")
plt.show()
