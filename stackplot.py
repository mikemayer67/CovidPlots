#!/usr/bin/env python3
"""
Plot weekly COVID cases in a stackeplot by state
"""

import common.args as cargs
import common.jhu_data as jhu
import argparse
import matplotlib.pyplot as plt

# Command Line Parser

parser = argparse.ArgumentParser(
        description = "Plots COVID cases in the JHU database as a stackplot of states"
        )

cargs.add_common(parser)

parser.set_defaults(sort='current', reversed=False, win=False, reload=False)

args = vars(parser.parse_args())

# JHU data

max_age = 0 if args['reload'] else 1
data = jhu.get_data(max_age)

sd = data['state']

if args['sort'] == 'current':
    states = sorted( 
            sd, 
            key=lambda x: sd[x]['weekly'][-1],
            reverse = args['reversed']
            )
    title = "States ordered by Most Recent Week's Cases"
else:
    states = sorted( 
            sd,
            key=lambda x: sd[x]['total'],
            reverse = args['reversed']
            )
    title = "States ordered by Total Cases to Date"

weeks = data['weeks']
cases = [ sd[state]['weekly'] for state in states ]

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
    
