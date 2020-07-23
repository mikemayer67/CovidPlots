#!/usr/bin/env python3
"""
Plot COVID cases in a pseudo-US map
"""

import common.args as cargs
import common.jhu_data as jhu
import common.states as states
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import sys
import math
import common.counties as cpop

# Command Line Parser
# 
# returns dictionary with values:
#     average:  (1-7)      [default=7]
#     win:      (true|false)
#     reload:   (true|false)
#     commonY:  (true|false)
#     output:   filename     [optional]
#

parser = argparse.ArgumentParser(
    description = "Plots COVID cases in the JHU database for all counties in the specified state"
    )

parser.add_argument('state')
parser.add_argument('-n','--average', type=int, choices=[1,2,3,4,5,6,7], default=7)
parser.add_argument('-y','--scale', choices=['common','per_capita'], default=None)

output = parser.add_mutually_exclusive_group()
output.add_argument('-o','--output', nargs=1, metavar='filename',
        help = "Name of file to save generated plot")
output.add_argument('-s','--show', dest='win', action='store_true',
        help = "Show the plot in popup window")

parser.add_argument('-r','--reload', action='store_true',
        help = "Do not use cached data")

parser.set_defaults(win=False, reload=False)

args = vars(parser.parse_args())

state = args['state'].upper()
if state not in states.abbrev_us_state:
    sys.exit("\n{} is not a recognized state postal code\n".format(state))


# JHU data

num_avg = args['average']

max_age = 0 if args['reload'] else 1
data = jhu.get_data(max_age)

dates = data['dates']
if state not in data['county']:
    sys.exit("\nCannot find county data for {}\n".format(state))

cd = data['county'][state]

timespan = "Plots cover period from {} to {}".format(dates[0],dates[-1])

# Filter data

ignore = [
        'Out of {}'.format(state), 
        'Unassigned',
        ]

counties = [x for x in cd.keys() if x not in ignore]
counties.sort()

max_Y = 0

for county in counties:
    raw = cd[county]['daily']

    if num_avg > 1:
        county_data = np.zeros([num_avg,raw.size + num_avg-1])
        for i in range(num_avg):
            county_data[i,i:i+raw.size] = raw
        county_data = sum(county_data)
        county_data = county_data[num_avg-1:raw.size]/num_avg
    else:
        county_data = raw

    if args['scale'] == 'per_capita':
        pop = cpop.population(county,state)
        county_data = county_data / pop

    cd[county]['daily'] = county_data

    max_Y = max(max_Y, max(county_data))

if args['win']:
    plt.ion()

x_values = [datetime.datetime.strptime(d,"%m/%d/%y").date() for d in dates]
x_formatter = mdates.DateFormatter('%m/%d')

max_Y = 1.1*max_Y

if args['scale'] == 'common':
    max_Y = round(max_Y, 1-int(math.floor(math.log10(max_Y))))
    y_span = "Plots show between 0 and {:,} new cases per day".format(int(max_Y))
elif args['scale'] == 'per_capita':
    y_span = "Plots show between 0 and {:.1f} new cases per day per 10,000 people".format(10000*max_Y)
else:
    y_span = None

n = len(counties)
nrow = math.ceil(math.sqrt(n * 0.75))
ncol = math.ceil(n/nrow)

fig, axs = plt.subplots(nrow, ncol)

for irow in range(nrow):
    for icol in range(ncol):
        i = irow*ncol + icol

        if i >= n:
            axs[irow][icol].axis('off')
            continue

        county = counties[i]

        y_values = cd[county]['daily']

        if args['scale']:
            max_y = max_Y
        else:
            max_y = 1.1*max(y_values)

        axs[irow,icol].plot(x_values[-y_values.size:],y_values)
        axs[irow,icol].set_xticks([])
        axs[irow,icol].set_yticks([])
        axs[irow,icol].set_ylim(0,1.1*max_y)
        axs[irow,icol].annotate(county,[0.0,0.8], xycoords='axes fraction')

axs[nrow-1,ncol-1].annotate(timespan,
        xy=(1,0), xycoords='figure fraction',
        xytext=(-5,5), textcoords='offset points',
        ha='right', va='bottom',
        fontsize='x-small',
        )

if y_span is not None:
    axs[nrow-1,ncol-1].annotate(y_span,
            xy=(0,0), xycoords='figure fraction',
            xytext=(5,5), textcoords='offset points',
            ha='left', va='bottom',
            fontsize='x-small',
            )
    
if args['scale'] == 'common':
    plt.suptitle('Covid-19 Trends in {} by County (common Y-axis)'.format(states.abbrev_us_state[state]))
elif args['scale'] == 'per_capita':
    plt.suptitle('Covid-19 Trends in {} by County (per capita)'.format(states.abbrev_us_state[state]))
else:
    plt.suptitle('Covid-19 Trends in {} by County (Y-axis normalized by County)'.format(states.abbrev_us_state[state]))

if args['win']:
    input("Press Enter to continue...")
else:
    plt.gcf().set_size_inches(12,8)
    filename = cargs.filename(args,'county_plot_{}_{}'.format(state,args['scale']))
    plt.savefig(filename,dpi=100)
    print("Plot saved to: " + filename)
