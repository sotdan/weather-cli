#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from collections import defaultdict
import os
import sys
import pyowm

from clint.textui import puts, colored

SUN = u'\u2600'
CLOUDS = u'\u2601'
RAIN = u'\u2602'
SNOW = u'\u2603'

class Arguments(object):
    QUERY = 'WEATHER'
    UNITS = 'WEATHER_UNITS'

    def __init__(self):
        self.units = defaultdict(lambda: 'fahrenheit', {'celsius': 'celsius'})

        self.parser = argparse.ArgumentParser(description="Outputs the weather for a given location query string")
        self.parser.add_argument('query', nargs="?", help="A location query string to find weather for")
        self.parser.add_argument('-u', '--units', dest='units', choices=self.units.keys(), help="Units of measurement (default: fahrenheit)")
        self.parser.add_argument('--iconify', action='store_true', help="Show weather in icons?")

    def parse(self, args, defaults={}):
        args = self.parser.parse_args(args)
        return {
            'query': args.query or defaults.get(Arguments.QUERY),
            'units': self.units[args.units or defaults.get(Arguments.UNITS)],
            'iconify': args.iconify,
        }

    def help(self):
        return self.parser.format_help()

def iconify(w):
    icon = w.get_weather_icon_name()
    codes = defaultdict(int, {
        '01d': SUN,
        '01n': SUN,
        '02d': CLOUDS,
        '02n': CLOUDS,
        '03d': CLOUDS,
        '03n': CLOUDS,
        '04d': CLOUDS,
        '04n': CLOUDS,
        '09d': RAIN,
        '09n': RAIN,
        '10d': RAIN,
        '10n': RAIN,
        '11d': RAIN,
        '11n': RAIN,
        '13d': SNOW,
        '13n': SNOW,
    })
    return codes[icon]

def get_temp_color(temperature):
    temp_color_map = [
        (40, 'cyan'),
        (60, 'blue'),
        (80, 'yellow')
    ]
    for color in temp_color_map:
        if temperature <= color[0]:
            return color[1]
    return 'red'

class Weather(object):

    @classmethod
    def main(cls):
        arguments = Arguments()

        args = arguments.parse(sys.argv[1:], defaults=os.environ)
        weather_provider = pyowm.OWM('b388ab985d247a3d54c0e981d0b24a9b') # OpenWeatherMap(formatter=formatter)

        if not args['query']:
            print arguments.help()
            sys.exit(1)

        try:
            observation = weather_provider.weather_at_place(args['query']) # now(args['query'], args['units'])
        except WeatherDataError as e:
            print >> sys.stderr, "ERROR: {0}".format(e.message)
            sys.exit(1)

        w = observation.get_weather()
        temp = w.get_temperature(args['units'])['temp']
        if args['iconify']:
            conditions = u"{0}\u00B0 {1}".format(
            temp,iconify(w))
        else:
            conditions = u"It's {0}\u00B0 and {1}".format(
            temp,w.get_status().lower())

        puts(getattr(colored, get_temp_color(temp))(conditions))


if __name__ == '__main__':
    Weather.main()
