#!/usr/bin/env python
import csv
from pprint import pprint
from collections import defaultdict
from functools import partial

import geojson
from geojson import Feature, FeatureCollection, Point


DATA_FILE = '/data/nyc-subway-entrance.csv'
PROPERTIES = [
    'Line',
    'Station Name',
    'North South Street',
    'East West Street',
    'Entrance Latitude',
    'Entrance Longitude',
]


def pluck(d, fields):
    return {f: d[f] for f in fields}


def load_all_exits():
    with open(DATA_FILE) as f:
        reader = csv.DictReader(f)
        exits = list(reader)
    return exits


def group_by_line_and_station(exits):
    listdict_creator = partial(defaultdict, list)
    subway_line_stations = defaultdict(listdict_creator)

    for exit in exits:
        line, station_name = exit['Line'], exit['Station Name']
        subway_line_stations[line][station_name].append(exit)

    return subway_line_stations


def check_station_latitudes(subway_line_stations):
    """
    Print out any stations whose exits list multiple station locations.
    (All station exits should have the same station location.)
    """
    for line, stations in subway_line_stations.items():
        for station_name, exits in stations.items():
            station_latitudes = [x['Station Latitude'] for x in exits]
            entrance_latitudes = [x['Entrance Latitude'] for x in exits]

            if len(set(station_latitudes)) > 1:
                print(station_name)
                print(station_latitudes)
                print(entrance_latitudes)
                print()

def export_to_geojson(subway_line_stations):
    features = []

    for line, stations in subway_line_stations.items():
        for station_name, exits in stations.items():
            for i, exit in enumerate(exits):
                # Create the point
                coords = (exit['Entrance Longitude'], exit['Entrance Latitude'])
                point = Point(tuple(map(float, coords)))

                # Create the features's properties
                properties = pluck(exit, PROPERTIES)
                properties['Exit Number'] = i + 1

                features.append(Feature(geometry=point, properties=properties))

    collection = FeatureCollection(features)
    print(geojson.dumps(collection))



def main():
    exits = load_all_exits()
    subway_line_stations = group_by_line_and_station(exits)
    export_to_geojson(subway_line_stations)

if __name__ == '__main__':
    main()
