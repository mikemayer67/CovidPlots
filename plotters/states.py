"""
Functions used for plotting the Covid state plots
"""

import sys

import support.jhu_data as jhu
import support.util as su
import support.states as sst
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def plot(args):
    
    jhu_data = jhu.JHUData(args.max_age)

    states = args.states

    plot_confirmed = 'confirmed' in args.data_type
    plot_deaths    = 'deaths'    in args.data_type

    dt = 'confirmed' if plot_confirmed else 'deaths'
    sort_data = jhu_data[dt]
    sort_data = sort_data.daily if args.sort_by == 'current' else sort_data.raw
    sort_data = { state:sort_data.state[state] for state in states }

    states = sorted(
        states,
        key = lambda state: sort_data[state][-1],
        reverse = not args.sort_ascending
    )

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

    x_values = su.x_values(dates)

    max_Y = max( [ v.max() for sd in data.values() for v in sd.values() ] )

    if args.yscale is not None:
        y_ticks, yscale = su.y_ticks(max_Y)

    title = '{} {}'.format(
        'New' if args.daily else 'Total',
        'Confirmed Cases and Deaths' if len(args.data_type)>1 else
        'Deaths' if 'deaths' in args.data_type else
        'Confirmed Cases'
    )


    if args.yscale == 'per_capita':
        ylabel = 'Counts per {:,} people'.format(int(yscale))
    else:
        ylabel = None

    for state in states:
        if args.show:
            plt.ion()

        if args.yscale is None:
            max_y = max( [ max(data[state][dt]) for dt in args.data_type ] )
            y_ticks, yscale = su.y_ticks(max_y)
        else:
            max_y = max_Y

        plt.gca().set_prop_cycle(None)
        plt.cla()

        for dt in args.data_type:
            plt.plot(x_values[dt],data[state][dt]*yscale)

        ax = plt.gca()
        plt.xticks(rotation=70)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        if args.yscale is not None:
            ax.set_ylim(0,1.1*max_y*yscale)
        plt.suptitle(sst.abbrev_us_state[state],fontsize='x-large')
        plt.title(title,fontsize='medium')
        if ylabel is not None:
            plt.ylabel(ylabel)
        plt.grid()

        if args.save:
            plt.gcf().set_size_inches(12,8)
            filename = args.filename(state=state)
            plt.savefig(filename,dpi=100)
            print("Plot saved to: " + filename)

        if args.show:
            if args.delay > 0:
                plt.pause(args.delay)
            else:
                input("Press Enter to continue...")



        
