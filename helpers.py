import os
import math
from matplotlib import pyplot as plt
import gpxpy
import gpxpy.gpx
import datetime as dt


def open_file(path: str) -> gpxpy.gpx.GPX:
    file = open(path, "r")
    return gpxpy.parse(file)


def point_coords_to_radians(point: gpxpy.gpx.GPXWaypoint):
    return point.latitude * (math.pi / 180), point.longitude * (math.pi / 180)


def haversine(point1: gpxpy.gpx.GPXWaypoint, point2: gpxpy.gpx.GPXWaypoint):
    # Returns difference in meters

    RADIUS = 6371000  # of earth in meters

    point1_lat, point1_long = point_coords_to_radians(point1)
    point2_lat, point2_long = point_coords_to_radians(point2)

    delta_lat = abs(point1_lat - point2_lat)
    delta_long = abs(point1_long - point2_long)

    a = (math.sin(delta_lat / 2)) ** 2 + math.cos(point1_lat) * math.cos(point2_lat) * (
        math.sin(delta_long / 2)
    ) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return RADIUS * c


def get_distance_points(segment: gpxpy.gpx.GPXTrackSegment) -> list[float]:
    sum = 0.0
    t = [0.0]
    for i in range(len(segment.points) - 1):
        sum += haversine(segment.points[i], segment.points[i + 1])
        t.append(sum)
    return t


def get_total_distance(segment: gpxpy.gpx.GPXTrackSegment) -> float:
    return sum(get_distance_points(segment))


def total_time(segment: gpxpy.gpx.GPXTrackSegment) -> dt.timedelta:
    points = segment.points
    total_time = dt.timedelta(0)

    for i in range(len(points) - 1):
        reversed_index = len(points) - 1 - i
        initial_time_str = points[reversed_index - 1].time
        final_time_str = points[reversed_index].time
        time_interval = final_time_str - initial_time_str
        total_time += time_interval

    return total_time


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
