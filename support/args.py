"""
Collection of functions for managing the command line inputs
"""

import argparse
import re
import time
import sys
import support.states as states

class Args:
    def __init__(self):
        args = vars(parse_args())

        for k,v in args.items():
            setattr(self,k,v)

        if self.data_type == None:
            self.data_type = ['confirmed']

        self.save = True if (self.saveas or self.saveas is None) else False

        if not self.save:
            self.show = True

        if hasattr(self,'state'):
            self.state = self.state.upper()
            if self.state not in states.abbrev_us_state.keys():
                print("\nUnrecognized state code: " + self.state + "\n")
                sys.exit(1)

        if hasattr(self,'states'):
            state_keys = states.abbrev_us_state.keys()
            if len(self.states) < 1:
                self.states = list(state_keys)
            else:
                self.states = [x.upper() for x in self.states]
                for state in self.states:
                    if state not in state_keys:
                        print("\nUnrecognized state code: " + state + "\n")
                        sys.exit(1)


    def filename(self, data_type=None, state=None):

        if data_type is None:
            data_type = 'combined' if len(self.data_type) > 1 else self.data_type[0]

        if state is None and hasattr(self,'state'):
            state = self.state

        if self.saveas:
            rval = self.saveas

            if state is not None:
                rval = re.sub('XX',state,rval)

        else:
            tm = time.localtime(time.time())
            tm = '{}{:02d}{:02d}'.format(tm.tm_year%100, tm.tm_mon, tm.tm_mday)

            rval = 'covid_{}_{}_{}'.format(tm,self.action,data_type)

            if state is not None:
                rval = rval + '_' + state

            if self.yscale is not None:
                rval = rval + '_' + self.yscale

            rval = rval + '.png'

        if not re.search('/',rval):
            rval = 'plots/' + rval

        return rval

########################################
# Free functions (not part of Args class)
########################################

def parse_args():

    parser = argparse.ArgumentParser(
        description="Plots COVID cases in the JHU database in a pseudo-US map",
        epilog = "."
    )

    common = common_args()
    yscale = yscale_args()
    sort   = sort_args()

    subparsers = parser.add_subparsers(
        dest='action',
        help = 'Type of plot to create')

    stack_parser = subparsers.add_parser(
        'stack',
        parents = [common, sort],
        help = 'Stack all states data on one nplot')

    state_parser  = subparsers.add_parser(
        'states',
        parents = [common, yscale, sort],
        epilog = "XX in filename will be replaced with state postal code",
        help = 'Plot cases for a given state or states')

    state_parser.add_argument('states',nargs=argparse.REMAINDER)
    state_parser.add_argument(
        '-delay', default=1, metavar='sec', type=int,
        help='How long to pause between states (0=wait for enter key)')

    county_parser = subparsers.add_parser(
        'counties',
        parents = [common, yscale],
        epilog = "XX in filename will be replaced with state postal code",
        help = 'Plot array of county plots for specified state')

    map_parser    = subparsers.add_parser(
        'map',
        parents = [common, yscale],
        help = 'Plot array of state plots in pseudo US map')

    county_parser.add_argument('state')

    return parser.parse_args()


def common_args():

    parser = argparse.ArgumentParser(add_help = False)

    parser.add_argument(
        '-deaths', dest='data_type', 
        action = 'append_const', const='deaths',
        help = 'Show number of deaths')
    parser.add_argument(
        '-confirmed', dest='data_type', 
        action = 'append_const', const='confirmed',
        help = 'Show number of confirmed cases (default)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-daily', dest='daily', action = 'store_true',
        help = 'Show daily counts (default)')
    group.add_argument(
        '-total', dest='daily', action = 'store_false',
        help = 'Show counts to date')
    parser.add_argument(
        '-save', dest='saveas', nargs='?', metavar='file',
        action = 'store', const = None, default=False,
        help = "Save the plot(s) to a file (filename is optional)")
    parser.add_argument(
        '-show', 
        action = 'store_true',
        help = "Display the plots on screen")
    parser.add_argument(
        '-reload', dest='max_age',
        action = 'store_const', const=0, default=86400,
        help = "Reload data from JHU (ignore any cached data)")

    parser.set_defaults(daily=True)

    return parser


def yscale_args():
    parser = argparse.ArgumentParser(add_help = False)

    parser.add_argument(
        '-smooth', type=int, metavar='days', default=3,
        help = 'Number of days averaged to smooth the curve (default=3)' )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-common', dest='yscale', 
        action = 'store_const', const='common',
        help = "Scale all plots equally based on actual counts")
    group.add_argument(
        '-percapita', dest='yscale', 
        action = 'store_const', const='per_capita',
        help = "Scale all plots equally based on population")

    return parser


def sort_args():

    parser = argparse.ArgumentParser(add_help = False)

    parser.add_argument(
        '-sort', dest='sort_by', metavar='?',
        choices=['current','total'], 
        help = "Count used to order states: current or total")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-ascending', dest='sort_ascending',
        action = 'store_true',
        help = "Sort the states in ascending order")
    group.add_argument(
        '-descending', dest='sort_ascending',
        action = 'store_false',
        help = "Sort the states in descending order")

    parser.set_defaults(sort_ascending=True, sort_by='current')

    return parser;


