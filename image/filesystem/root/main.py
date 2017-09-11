#!/usr/bin/env python
import csv
import json
from pprint import pprint
from collections import defaultdict
from functools import partial

import click
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

# Correction structure:
# Exits from the first station should be place in the second station
CORRECTIONS = (
    (('Nassau', 'Essex St'),
     ('6 Avenue', 'Delancey St')),

    (('4 Avenue', '9th St'),
     ('6 Avenue', '4th Av')),

    (('Broadway', 'Lawrence St'),
     ('Fulton', 'Jay St - Borough Hall')),

    (('8 Avenue', '59th St'),
     ('Broadway-7th Ave', '59th St-Columbus Circle')),

    (('Flushing', '5th Av'),
     ('6 Avenue', '42nd St')),

    (('42nd St Shuttle', 'Times Square'),
     ('Broadway-7th Ave', 'Times Square')),

    (('Broadway', 'Times Square-42nd St'),
     ('Broadway-7th Ave', 'Times Square')),

    (('8 Avenue', '42nd St'),
     ('Broadway-7th Ave', 'Times Square')),

    (('42nd St Shuttle', 'Grand Central'),
     ('Lexington', 'Grand Central-42nd St')),

    (('Flushing', 'Grand Central-42nd St'),
     ('Lexington', 'Grand Central-42nd St')),
)


def correct(line, station_name):
    for incorrect, correct in CORRECTIONS:
        if (line, station_name) == incorrect:
            return correct
    return (line, station_name)


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
        line, station_name = correct(exit['Line'], exit['Station Name'])
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

def print_geojson(subway_line_stations):
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
    print(geojson.dumps(collection, indent=2))


def get_station_lines(exit):
    line_fields = ['Route{}'.format(i) for i in range(1, 12)]

    lines = []
    for field in line_fields:
        line = exit[field]
        if line:
            lines.append(line)

    return lines

def all_station_coordinates(subway_line_stations):
    station_coordinates = {}

    for line, stations in subway_line_stations.items():
        for station, exits in stations.items():
            arbitrary_exit = exits[0]
            lines = get_station_lines(arbitrary_exit)
            station_key = "{} ({})".format(station, ' '.join(lines))
            coordinates = {
                'longitude': arbitrary_exit['Station Longitude'],
                'latitude': arbitrary_exit['Station Latitude']
            }

            station_coordinates[station_key] = coordinates

    return station_coordinates


@click.group()
@click.pass_context
def cli(context):
    exits = load_all_exits()
    context.obj['subway_line_stations'] = group_by_line_and_station(exits)


@cli.command('map-geojson')
@click.pass_context
def map_data(context):
    print_geojson(context.obj['subway_line_stations'])


@cli.command('frontend-json')
@click.pass_context
def frontend_data(context):
    station_coords = all_station_coordinates(context.obj['subway_line_stations'])
    print(json.dumps(station_coords))


if __name__ == '__main__':
    cli(obj={})
