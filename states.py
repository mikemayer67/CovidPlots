#!/usr/bin/env python3
"""
Plot weekly COVID cases as series of bar graphs
"""

import common.args as cargs
import common.jhu_data as jhu
import common.states as states
import common.util as cu
import argparse
import matplotlib.pyplot as plt
import numpy as np
import math
import sys

# Command Line Parser
#    Command line parser for stateplot.py
#
#    returns dictionary with values:
#        sort:     (total|current)
#        reversed: (true|false)
#        win:      (true|false)
#        reload:   (true|false)
#        commonY:  (true|false)
#        logY:     (true|false)
#        output:   filename     [optional]

parser = argparse.ArgumentParser(
    description = "Plots COVID cases in the JHU database as a sereis bar charts",
    epilog = "XXX in a filename will be replaced by state's postal code"
    )

cargs.add_common(parser)

parser.add_argument('states',nargs=argparse.REMAINDER)

parser.add_argument('-l','--logY', action='store_true',
        help = "Plot weekly counts on a log scale")

common_y = parser.add_mutually_exclusive_group()
common_y.add_argument('-y','--commonY', dest='commonY', action='store_true',
        help = "Use same Y axis for all states")
common_y.add_argument('-Y','--rescaleY', dest='commonY', action='store_false',
        help = "Use resscale Y axis for each state")

parser.set_defaults(sort='current', reversed=False, win=False, reload=False,
        logY=False,commonY=True)

args = vars(parser.parse_args())

args['states'] = [ x.upper() for x in args['states'] ]

for state in args['states']:
    if state not in states.abbrev_us_state:
        sys.exit("\n{} is not a recognized state postal code\n".format(state))

# JHU data

max_age = 0 if args['reload'] else 1
data = jhu.get_data(max_age)
sd   = data['state']

if len(args['states']) > 0:
    states = args['states']
else:
    states = sd.keys()

weekly = { state:sd[state]['weekly'] for state in states }
total  = { state:sd[state]['total']  for state in states }

if args['sort'] == 'current':
    states = [ x[0] for x in 
        sorted( 
        weekly.items(),
        key = lambda x: x[1][-1],
        reverse = args['reversed']
        ) ]
    title = "States ordered by Most Recent Week's Cases"
else:
    states = [ x[0] for x in 
        sorted( 
        total.items(),
        key = lambda x: x[1],
        reverse = args['reversed']
        ) ]
    title = "States ordered by Total Cases to Date"

weeks = data['weeks']

ind   = np.arange(len(weeks))

if args['commonY']:
    max_y = max( [v.max() for (k,v) in weekly.items() ] )
    y     = cu.y_ticks( max_y)

subtitle = "Shown in order of {} {} cases".format(
        'decreasing'  if args['reversed']          else 'increasing',
        'most recent' if args['sort'] == 'current' else 'total'
        )

for state in states:
    if args['win']:
        plt.ion()

    if not args['commonY']:
        max_y = weekly[state].max()

    plt.gca().set_prop_cycle(None)
    plt.cla()
    plt.bar(ind, weekly[state], 0.4)
    plt.xlabel("Week")
    plt.ylabel("Weekly New Cases")
    plt.xticks(ind,weeks)

    if args['logY']:
        plt.gca().set_yscale('log')
        plt.ylim(1,1.5*max_y)
    else:
        y = cu.y_ticks(max_y)
        plt.yticks(y)

    plt.suptitle(state, fontsize=14)
    plt.title(subtitle, fontsize=10)

    if args['win']:
        plt.pause(1.0)
    else:
        plt.gcf().set_size_inches(12,8)
        filename = cargs.filename(args,'bar',state)
        plt.savefig(filename,dpi=100)
        print("Plot saved to: " + filename)

if args['win']:
    input("Press Enter to continue...")
