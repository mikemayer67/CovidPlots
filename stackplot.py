#!/usr/bin/env python
"""
Plot weekly COVID cases in a stackeplot by state
"""

import common.args as cargs
import common.jsu_data as jsu
import matplotlib.pyplot as plt

args = cargs.stackplot()

max_age = 0 if args['reload'] else 1
data = jsu.get_data(max_age)

if args['sort'] == 'current':
    states = [ x[0] for x in 
        sorted( 
        data['weekly'].items(),
        key = lambda x: x[1][-1],
        reverse = args['reversed']
        ) ]
    title = "States ordered by Most Recent Week's Cases"
else:
    states = [ x[0] for x in 
        sorted( 
        data['total'].items(),
        key = lambda x: x[1],
        reverse = args['reversed']
        ) ]
    title = "States ordered by Total Cases to Date"

weeks = data['dates']
cases = [ data['weekly'][state] for state in states ]

if args['win']:
    plt.ion()

plt.stackplot(weeks,cases)
plt.legend(states,loc='upper left',ncol=2,fontsize='xx-small')
plt.xlabel("Week")
plt.ylabel("Weekly New Cases")
plt.gca().set_title(title)

if args['win']:
    input("Press Enter to continue...")
else:
    plt.gcf().set_size_inches(12,8)
    filename = cargs.filename(args,'stackplot')
    plt.savefig(filename,dpi=100)
    print("Plot saved to: " + filename)
    
