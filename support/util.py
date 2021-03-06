"""
Collection of utililty functions that support multiple plot scripts

This file can be imported and contains the following functions:

    * y_ticks   - computes aesthetically pleasing y-axis tick marks
"""

import math
import numpy as np
from datetime import datetime


def x_values(dates):
    """
    Converts a list of date strings to datetime dates

    If multiplt lists are provided (via dict), the conversion will
    be applied to all lists and returned in a dictionary with the
    same keys as the input dictionary
    """
    if isinstance(dates,dict):
        return { k:x_values(v) for k,v in dates.items() }
    else:
        return [ datetime.strptime(d,"%m/%d/%y").date() for d in dates ]

def timespan(dates):
    """
    Converts a list of date strings to a timespan

    If multiplt lists are provided (via dict), the returned timespan
    will be based on the union of the lists
    """
    if isinstance(dates,dict):
        rval = [
            min( [ datetime.strptime(d[ 0],"%m/%d/%y").date() for d in dates.values() ] ),
            max( [ datetime.strptime(d[-1],"%m/%d/%y").date() for d in dates.values() ] )
        ]

    else:
        rval = [
            datetime.strptime(dates[ 0],"%m/%d/%y").date(),
            datetime.strptime(dates[-1],"%m/%d/%y").date(),
        ]

    rval = [ dt.strftime("%d-%b-%y") for dt in rval ]

    return rval


def y_ticks(max_y):
    """
    Computes aesthetically pleasing y-axis tick marks for specified max value
    
    Note:: will always include y=0 as the minimum value

    returns list of y values and scaling factor
    """

    log_max = math.log10(max_y)
    m_log_y = math.floor(log_max)       # log of mantissa 
    c_log_y = log_max - m_log_y  # log of characteristic

    sf = 1.0
    while m_log_y < 1:
        m_log_y += 1
        sf *= 10

    m_y     = 10 ** m_log_y      # mantissa
    c_y     = 10 ** c_log_y      # characteristic

    if c_y <= 2.5: 
        d_y = 0.1 * m_y
    elif c_y <= 3: 
        d_y = 0.2 * m_y
    elif c_y <= 7: 
        d_y = 0.5  * m_y
    else:          
        d_y = 1.0  * m_y

    n_y = 2 + int(sf*max_y/d_y)

    return [x * d_y for x in range(0, n_y)], sf
