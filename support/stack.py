"""
Functions used for plotting the Covid stack plot
"""

import sys
import support.jhu_data as jhu
import matplotlib.pyplot as plt
import numpy as np

def plot(args):

    if len(args.data_type) > 1:
        print("\nCannot plot both deaths and cases in a stack plot\n");
        sys.exit(1)

    data_type = args.data_type[0]

    data = jhu.get_data( data_type, args.max_age )
        
    sd = data['state']

    if args.sort_by == 'current':
        states = sorted( 
                sd, 
                key=lambda x: sd[x]['weekly'][-1],
                reverse = not args.sort_ascending
                )
    else:
        states = sorted( 
                sd,
                key=lambda x: sd[x]['total'],
                reverse = not args.sort_ascending
                )

    title = '{} (ordered by {})'.format(
        "New COVID Cases" if data_type == 'confirmed' else 'COVID deaths' ,
        "most recent count" if args.sort_by == 'current' else "total cases"
    )

    ylabel = 'Weekly {}'.format(
        "New Cases" if data_type == 'confirmed' else 'Deaths'
    )

    weeks = data['weeks']

    if args.daily:
        cases = [ sd[state]['weekly'] for state in states ]
    else:
        cases = [ np.cumsum(sd[state]['weekly']) for state in states ]

    if args.show:
        plt.ion()

    plt.stackplot(weeks,cases)
    plt.legend(states,loc='upper left',ncol=2,fontsize='xx-small')
    plt.xticks(rotation=-90)
    plt.xlabel("Week")
    plt.ylabel(ylabel)
    plt.gca().set_title(title)

    if args.save:
        plt.gcf().set_size_inches(12,8)
        filename = args.filename()
        plt.savefig(filename,dpi=100)
        print("Plot saved to: " + filename)

    if args.show:
        input("Press Enter to continue...")
