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
import math

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
    description = "Plots COVID cases in the JHU database in a pseudo-US map"
    )

parser.add_argument('-n','--average', type=int, [1,2,3,4,5,6,7], default=7)
parser.add_argument('-y','--scale', choices=['common','per_capita'], default=None)

data_type = parser.add_mutually_exclusive_group()
data_type.add_argument('-D','--deaths', dest='data_type', action='store_const', const='deaths',
        help = "Display deaths rather than confirmed cases")
data_type.add_argument('-C','--cases', dest='data_type', action='store_const', const='confirmed',
        help = "Display confirmed cases rather than deaths")
    
output = parser.add_mutually_exclusive_group()
output.add_argument('-o','--output', nargs=1, metavar='filename',
        help = "Name of file to save generated plot")
output.add_argument('-s','--show', dest='win', action='store_true',
        help = "Show the plot in popup window")

parser.add_argument('-r','--reload', action='store_true',
        help = "Do not use cached data")

parser.set_defaults(data_type='confirmed',win=False, reload=False)

args = vars(parser.parse_args())

# JHU data

num_avg   = args['average']
data_type = args['data_type']

max_age = 0 if args['reload'] else 1
data = jhu.get_data(data_type,max_age)

dates = data['dates']
sd    = data['state']

timespan = "Plots cover period from {} to {}".format(dates[0],dates[-1])

plot_map = np.array( [
    ['AK',''  ,''  ,''  ,''  ,'WI',''  ,''  ,'VT','NH','ME'],
    ['WA','ID','MT','ND','MN','IL','MI',''  ,'NY','MA',''  ],
    ['OR','NV','WY','SD','IA','IN','OH','PA','NJ','CT','RI'],
    ['CA','UT','CO','NE','MO','KY','WV','VA','MD','DE',''  ],
    [''  ,'AZ','NM','KS','AR','TN','NC','SC','DC',''  ,''  ],
    [''  ,''  ,''  ,'OK','LA','MS','AL','GA',''  ,''  ,''  ],
    ['HI',''  ,''  ,'TX',''  ,''  ,''  ,''  ,'FL',''  ,'PR']
    ])

max_Y = 0

for state in sd.keys():
    raw = sd[state]['daily']

    if num_avg > 1:
        state_data = np.zeros([num_avg,raw.size + num_avg-1])
        for i in range(num_avg):
            state_data[i,i:i+raw.size] = raw
        state_data = sum(state_data)
        state_data = state_data[num_avg-1:raw.size]/num_avg
    else:
        state_data = raw

    if args['scale'] == 'per_capita':
        pop = states.abbrev_population[state]
        state_data = state_data / pop
        
    sd[state]['daily'] = state_data

    max_Y = max(max_Y, max(state_data))

if args['win']:
    plt.ion()

x_values = [datetime.datetime.strptime(d,"%m/%d/%y").date() for d in dates]
x_formatter = mdates.DateFormatter('%m/%d')

max_Y = 1.1*max_Y

if data_type == 'deaths':
    plot_label = 'deaths'
else:
    plot_label = 'new cases'

if args['scale'] == 'common':
    max_Y = round(max_Y, 1-int(math.floor(math.log10(max_Y))))
    y_span = "Plots show between 0 and {:,} {} per day".format(int(max_Y), plot_label)
elif args['scale'] == 'per_capita':
    y_span = "Plots show between 0 and {:.1f} {} per day per 100,000 people".format(100000*max_Y, plot_label)
else:
    y_span = None

nrow, ncol = plot_map.shape
fig, axs = plt.subplots(nrow, ncol)

for row in range(nrow):
    for col in range(ncol):
        state = plot_map[row,col]
        if state not in states.abbrev_us_state:
            axs[row][col].axis('off')
            continue

        y_values = sd[state]['daily']

        if args['scale']:
            max_y = max_Y
        else:
            max_y = 1.1*max(y_values)

        axs[row,col].plot(x_values[-y_values.size:],y_values)
        axs[row,col].set_xticks([])
        axs[row,col].set_yticks([])
        axs[row,col].set_ylim(0,max_y)
        axs[row,col].annotate(state,[0.0,0.8], xycoords='axes fraction')
    
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
    scale_type = 'common Y-axis'
elif args['scale'] == 'per_capita':
    scale_type = 'per capita'
else:
    scale_type = 'Y-axis scaled by state'

plot_title = 'Covid-19 {} by State ({})'.format(plot_label.title(),scale_type)
plt.suptitle(plot_title)

if args['win']:
    input("Press Enter to continue...")
else:
    plt.gcf().set_size_inches(12,8)
    filename = cargs.filename(args,'mapplot_{}'.format(args['scale']))
    plt.savefig(filename,dpi=100)
    print("Plot saved to: " + filename)
