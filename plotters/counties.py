"""
Functions used for plotting the Covid stack plot
"""

import sys

import support.jhu_data as jhu
import support.util as su
import support.states as sst
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def plot(args):

    plot_deaths    = 'deaths'    in args.data_type
    plot_confirmed = 'confirmed' in args.data_type

    state = args.state

    jhu_data = jhu.JHUData(args.max_age)

    frequency = 'daily' if args.daily else 'raw'
    data = jhu_data.get_county_data(
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

    title = '{} {} Covid-19 {} by County'.format(
        'New' if args.daily else 'Total',
        sst.abbrev_us_state[state],
        'Confirmed Cases and Deaths' if plot_deaths and plot_confirmed else
        'Deaths' if plot_deaths else 'Confirmed Cases'
    )
    if args.yscale == 'per_capita':
        title += ' (per capita)'

    n = len(data)
    nrow = math.ceil(math.sqrt(n * 0.75))
    ncol = math.ceil(n/nrow)

    fig, axs = plt.subplots(nrow, ncol)

    irow = 0
    icol = 0
    for county, cd in data.items():

        if args.yscale is None:
            max_y = max( [ max(cd[dt]) for dt in args.data_type ] )
            y_ticks, yscale = su.y_ticks(max_y)
        else:
            max_y = max_Y

        for dt in args.data_type:
            x = x_values[dt]
            y = cd[dt]*yscale
            axs[irow,icol].plot(x,y)
            axs[irow,icol].set_ylim(0,1.1*max_y*yscale)
            axs[irow,icol].set_xticks([])
            axs[irow,icol].set_yticks([])
            axs[irow,icol].annotate(
                county,[0.0,0.8], 
                xycoords='axes fraction',
                fontsize='x-small')

        icol += 1
        if icol == ncol:
            icol = 0
            irow += 1

    while irow < nrow:
        while icol < ncol:
            axs[irow][icol].axis('off')
            icol += 1
        icol = 0
        irow += 1

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
        y_span = "Each county is scaled individually to fill the plot"

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
