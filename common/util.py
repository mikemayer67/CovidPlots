"""
Collection of utililty functions that support multiple plot scripts

This file can be imported and contains the following functions:

    * y_ticks   - computes aesthetically pleasing y-axis tick marks
"""

import math

def y_ticks(max_y):
    """
    Computes aesthetically please y-axis tick marks for specified max value
    
    Note:: will always include y=0 as the minimum value

    returns list of y values
    """

    log_max = math.log10(max_y)
    m_log_y = int(log_max)       # log of mantissa 
    c_log_y = log_max - m_log_y  # log of characteristic

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

    n_y = 2 + int(max_y/d_y)

    return list(range(0, int(n_y * d_y), int(d_y)))
