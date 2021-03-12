"""
Functions used for plotting the Covid stack plot
"""

import sys
import support.jhu_data as jhu
import matplotlib.pyplot as plt
import numpy as np

import support.states as sst

def plot(args):

    if len(args.data_type) > 1:
        print("\nCannot plot both deaths and cases in a stack plot\n");
        sys.exit(1)

    data_type = args.data_type[0]

    data = jhu.JHUData( args.max_age )
    data = data[data_type]
        
    if args.sort_by == 'current':
        sd = data.weekly.state
    else:
        sd = data.raw.state

    states = sorted( 
        sd, 
        key=lambda x: sd[x][-1],
        reverse = not args.sort_ascending
    )

    title = '{} {} (ordered by {})'.format(
        "New" if args.daily else "Total",
        "COVID Cases" if data_type == 'confirmed' else 'COVID deaths' ,
        "most recent count" if args.sort_by == 'current' else "total cases"
    )

    ylabel = '{} {}'.format(
        "New" if args.daily else "Total",
        "Cases" if data_type == 'confirmed' else 'Deaths'
    )

    weeks = data.weeks

    cases = [ data.weekly.state[state] for state in states ]

    if not args.daily:
        cases = [ np.cumsum(x) for x in cases ]

    if args.show:
        plt.ion()

    fig = plt.figure(figsize=(12,8))
    fig.add_subplot(1,1,1)

    plt.stackplot(weeks,cases)
    plt.legend(states,loc='upper left',ncol=2,fontsize='xx-small')
    plt.xticks(rotation=-90)
    plt.xlabel("Week")
    plt.ylabel(ylabel)
    plt.title(title)

    if not args.daily:
        yl = [ 100*x/sst.us_population for x in plt.gca().get_ylim() ]
        ax2 = plt.twinx()
        plt.ylim(yl)
        ax2.yaxis.set_major_formatter(lambda x,_: f'{x:.1f}%')

    if args.save:
        plt.gcf().set_size_inches(12,8)
        filename = args.filename()
        plt.savefig(filename,dpi=100)
        print("Plot saved to: " + filename)

    if args.show:
        input("Press Enter to continue...")
