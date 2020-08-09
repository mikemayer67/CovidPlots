"""
Functions used for plotting the Covid stack plot
"""

import sys

import support.jhu_data as jhu
import support.util as su
import support.states as sst
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def plot(args):

    plot_deaths    = 'deaths'    in args.data_type
    plot_confirmed = 'confirmed' in args.data_type

    jhu_data = jhu.JHUData(args.max_age)

    plot_map = np.array( [
        ['AK',''  ,''  ,''  ,''  ,'WI',''  ,''  ,'VT','NH','ME'],
        ['WA','ID','MT','ND','MN','IL','MI',''  ,'NY','MA',''  ],
        ['OR','NV','WY','SD','IA','IN','OH','PA','NJ','CT','RI'],
        ['CA','UT','CO','NE','MO','KY','WV','VA','MD','DE',''  ],
        [''  ,'AZ','NM','KS','AR','TN','NC','SC','DC',''  ,''  ],
        [''  ,''  ,''  ,'OK','LA','MS','AL','GA',''  ,''  ,''  ],
        ['HI',''  ,''  ,'TX',''  ,''  ,''  ,''  ,'FL',''  ,'PR']
        ])

    states = [x for x in plot_map.reshape(-1) if x != '']


    frequency = 'daily' if args.daily else 'raw'
    data = dict()
    for state in states:
        data[state] = jhu_data.get_state_data(
            state, 
            data_type=args.data_type,
            frequency=frequency,
            smooth=args.smooth,
            yscale=args.yscale,
        )

    dates = jhu_data.get_dates(
        data_type=args.data_type,
        frequency=frequency,
        smooth=args.smooth)

    timespan = su.timespan(dates)
    timespan = "Plots cover period from {} to {}".format(timespan[0],timespan[-1])

    x_values = su.x_values(dates)


    max_Y = max( [ v.max() for sd in data.values() for v in sd.values() ] )

    if args.yscale is not None:
        y_ticks, yscale = su.y_ticks(max_Y)

    title = '{} Covid-19 {} by State'.format(
        'New' if args.daily else 'Total',
        'Confirmed Cases and Deaths' if plot_deaths and plot_confirmed else
        'Deaths' if plot_deaths else 'Confirmed Cases'
    )
    if args.yscale == 'per_capita':
        title += ' (per capita)'


    nrow, ncol = plot_map.shape
    fig, axs = plt.subplots(nrow, ncol)

    if args.show:
        plt.ion()

    for row in range(nrow):
        for col in range(ncol):
            state = plot_map[row,col]
            if state not in states:
                axs[row,col].axis('off')
                continue

            if args.yscale is None:
                max_y = max( [ max(data[state][dt]) for dt in args.data_type ] )
                y_ticks, yscale = su.y_ticks(max_y)
            else:
                max_y = max_Y

            for dt in args.data_type:
                x = x_values[dt]
                y = data[state][dt]*yscale
                axs[row,col].plot(x,y)
                axs[row,col].set_ylim(0,1.1*max_y*yscale)
                axs[row,col].set_xticks([])
                axs[row,col].set_yticks([])
                axs[row,col].annotate(state,[0.0,0.8], xycoords='axes fraction')

    plt.suptitle(title)

    axs[nrow-1,ncol-1].annotate(timespan,
            xy=(1,0), xycoords='figure fraction',
            xytext=(-5,5), textcoords='offset points',
            ha='right', va='bottom',
            fontsize='x-small',
            )

    if args.yscale == 'common':
        y_span = "Plots show between 0 and {:,} {}{}".format(
            int( y_ticks[-1] ),
            'cases' if plot_confirmed else 'deaths',
            ' per day' if args.daily else '')
    elif args.yscale == 'per_capita':
        y_span = "Plots show between 0 and {} {}{} per {:,} people".format(
            int(yscale * max_Y),
            'cases' if plot_confirmed else 'deaths',
            ' per day' if args.daily else '',
            int(yscale))
    else:
        y_span = "Each state is scaled individually to fill the plot"

    axs[nrow-1,ncol-1].annotate(y_span,
        xy=(0,0), xycoords='figure fraction',
        xytext=(5,5), textcoords='offset points',
        ha='left', va='bottom',
        fontsize='x-small',
        )

    plt.gcf().set_size_inches(12,8)

    if args.save:
        filename = args.filename()
        plt.savefig(filename,dpi=100)
        print("Plot saved to: " + filename)

    if args.show:
        plt.show()
        input("Press Enter to exit...")
