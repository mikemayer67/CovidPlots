#!/usr/bin/env python
"""
Plot weekly COVID cases as series of bar graphs
"""

import common.args as cargs
import common.jsu_data as jsu
import common.states as states
import common.util as cu
import matplotlib.pyplot as plt
import numpy as np
import math

args = cargs.stateplot()

max_age = 0 if args['reload'] else 1
data = jsu.get_data(max_age)

weekly = data['weekly']
total = data['total']

if len(args['states']) > 0:
    weekly = { k:v for (k,v) in weekly.items() if states.us_state_abbrev[k] in args['states'] }
    total = { k:v for (k,v) in total.items() if states.us_state_abbrev[k] in args['states'] }

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

weeks = data['dates']

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
