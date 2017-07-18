#!/usr/bin/env python
import csv
from pprint import pprint
from collections import defaultdict
from functools import partial

import geojson


FIELDS = [
    'Line',
    'Station Name',
    'Station Latitude',
    'Station Longitude',
    'North South Street',
    'East West Street',
    'Entrance Latitude',
    'Entrance Longitude',
]


def pluck(d):
    return {f: d[f] for f in FIELDS}


# Load the data
with open('/data/nyc-subway-entrance.csv', 'r') as f:
    reader = csv.DictReader(f)
    exits = list(reader)

# pprint(exits[0])

# print('----------------------------------------------')

listdict_creator = partial(defaultdict, list)
subway_lines = defaultdict(listdict_creator)

for exit in exits:
    line, station_name = exit['Line'], exit['Station Name']
    subway_lines[line][station_name].append(exit)


# pprint([pluck(x) for x in subway_lines['6 Avenue']['East Broadway']])

# print('----------------------------------------------')

for line, stations in subway_lines.items():
    for station_name, exits in stations.items():
        station_latitudes = [x['Station Latitude'] for x in exits]
        entrance_latitudes = [x['Entrance Latitude'] for x in exits]
        if len(set(station_latitudes)) > 1:
            print(station_name)
            print(station_latitudes)
            print(entrance_latitudes)
            # pprint(exits)
            print()
