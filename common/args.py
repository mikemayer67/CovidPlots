"""
Collection of functions for parsing command line arguments

This file can be imported and contains the following functions:

    * stackplot - supports stackplot.py
    * stateplot - supports stateplot.py
    * mapplot   - supports mapplot.py

    * filename  - returns plot filename
"""

import argparse
import re
import time
import sys
import common.states as states


def add_common(parser):
    sort_type = parser.add_mutually_exclusive_group()
    sort_type.add_argument('-t','--total',   dest='sort', action='store_const', const='total',
            help = "Sort states based on total cases to date")
    sort_type.add_argument('-c','--current', dest='sort', action='store_const', const='current',
            help = "Sort states based on current new cases count")
    
    sort_order = parser.add_mutually_exclusive_group()
    sort_order.add_argument('-a','--ascending', dest='reversed', action='store_false',
            help = "Sort states in ascending order [default]")
    sort_order.add_argument('-d','--descending', dest='reversed', action='store_true',
            help = "Sort states in descending order")
    
    output = parser.add_mutually_exclusive_group()
    output.add_argument('-o','--output', nargs=1, metavar='filename',
            help = "Name of file to save generated plot")
    output.add_argument('-s','--show', dest='win', action='store_true',
            help = "Show the plot in popup window")

    parser.add_argument('-r','--reload', action='store_true',
            help = "Do not use cached data")


def filename(args,plot_type,state=None):
    """
    Determines filename for plot file given command line arguments

    given:
        args:      arg dictionary (returned from one of the _args functions
        plot_type: type of plot (stacked|bar|animated) 
        state:     name of state   [default = None]

    returns filename
    """

    if state is not None:
        if state in states.us_state_abbrev:
            state = states.us_state_abbrev[state]

    filename = args['output']
    if filename is not None:
        filename = filename[0]
        if state is None:
            pass
        elif re.search('XXX',filename):
            filename = re.sub('XXX',state,filename)
        elif re.search('\.[^.]+$',filename):
            filename = re.sub('(\.[^.]+)$',r'_XXX\1',filename)
            filename = re.sub('XXX',state,filename)
        else:
            filename = filename + "." + state
    else: 
        tm = time.localtime(time.time())
        filename = ['covid']

        filename.append("{}{:02d}{:02d}".format(tm.tm_year%100, tm.tm_mon, tm.tm_mday))

        filename.append(plot_type)

        if args.get('logY',False):
            filename.append('log')

        if 'commonY' in args:
            if not args['commonY']:
                filename.append('rescaled')

        if state is not None:
            filename.append(state)

        filename = '_'.join(filename)

        filename  = filename + '.png'

    if not re.search('/',filename):
        filename = "plots/" + filename

    return filename

            


