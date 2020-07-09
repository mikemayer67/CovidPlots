#!/usr/bin/env python3
"""
Plot COVID cases in a pseudo-US map
"""

import common.args as cargs
import common.jsu_data as jsu
import common.states as states
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

args = cargs.mapplot()

num_avg = args['average']

max_age = 0 if args['reload'] else 1
data = jsu.get_data(max_age)

dates = data['dates']
daily = data['daily']

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

for state in daily.keys():
    if num_avg > 1:
        raw = daily[state]
        state_data = np.zeros([num_avg,raw.size + num_avg-1])
        for i in range(num_avg):
            state_data[i,i:i+raw.size] = raw
        state_data = sum(state_data)
        state_data = state_data[num_avg-1:raw.size]/num_avg

        if( args['scale'] == 'per_capita' ):
            pop = states.us_state_population[state]
            state_data = state_data / pop
            
        daily[state] = state_data

        max_y = max(state_data)
        if max_y > max_Y:
            max_Y = max_y

if args['win']:
    plt.ion()

x_values = [datetime.datetime.strptime(d,"%m/%d/%y").date() for d in dates]
x_formatter = mdates.DateFormatter('%m/%d')

nrow, ncol = plot_map.shape
fig, axs = plt.subplots(nrow, ncol)

for state in daily.keys():
    for row in range(nrow):
        for col in range(ncol):
            abbrev = plot_map[row,col]
            if abbrev not in states.abbrev_us_state:
                axs[row][col].axis('off')
                continue
            state = states.abbrev_us_state[abbrev]
            if state not in daily:
                axs[row][col].axis('off')
                continue

            y_values = daily[state]

            if args['scale'] == 'by_state':
                max_y = max(y_values)
            else:
                max_y = max_Y

            axs[row,col].plot(x_values[-y_values.size:],daily[state])
            axs[row,col].set_xticks([])
            axs[row,col].set_yticks([])
            axs[row,col].set_ylim(0,1.1*max_y)
            axs[row,col].annotate(abbrev,[0.0,0.8], xycoords='axes fraction')
    
if args['scale'] == 'common':
    plt.suptitle('Covid-19 Trends by State (common Y-axis)')
elif args['scale'] == 'per_capita':
    plt.suptitle('Covid-19 Trends by State (per capita)')
else:
    plt.suptitle('Covid-19 Trends by State (Y-axis normalized by state)')

if args['win']:
    input("Press Enter to continue...")
else:
    plt.gcf().set_size_inches(12,8)
    filename = cargs.filename(args,'mapplot_{}'.format(args['scale']))
    plt.savefig(filename,dpi=100)
    print("Plot saved to: " + filename)
