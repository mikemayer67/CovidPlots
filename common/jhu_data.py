"""
Collection of functions for managing the data from JHU (Johns Hopkins)

This file can be imported and contains the following functions:

    * get_data:  Return JHU data
"""

import numpy as np
import requests
import csv
import pickle
import time
import common.states as states

from contextlib import closing

def get_data( max_age = 1 ):
    """
    Returns JHU data

    If cached data is available and isn't too old, it will be returned.
    Otherwise, the data will be retrieved from the JHU github repository.

    Arguments:
       max_age:  maximum age in hours before cached data "expires" [default = 1]
    """

    # return cached data if available

    now = time.time()

    try:
        with open('data/jhu.np',mode='rb') as fp:
            data = pickle.load(fp)
            ts = data['timestamp']
        if now < ts + 3600 * max_age:
            print("Using cached data from download at " + time.ctime(ts))
            return data
    except Exception as e:
        pass

    # No? Download new data

    max_weekly = 0
    state_data  = dict()  # data indexed by state
    county_data = dict()  # data indexed by state/county

#    daily  = dict()  # daily totals profile indexed by state
#    weekly = dict()  # weekly totals profile indexed by state
#    total  = dict()  # total cases indexd by state

    url = '/'.join( [ "https://raw.githubusercontent.com",
                      "CSSEGISandData",
                      "COVID-19",
                      "master",
                      "csse_covid_19_data",
                      "csse_covid_19_time_series",
                      "time_series_covid19_confirmed_US.csv"] )

    rq = requests.get(url,stream=True)
    with closing(rq) as r:
        f = ( line.decode('utf-8') for line in r.iter_lines() )
        reader = csv.reader(f, delimiter=',',quotechar='"')
        columns = next(reader)
        dates = np.array(columns[55:])  # skip roughly first 2 months of data

        # we need to ensure an extra day of data for diff
        ndays  = dates.size - 1   # make sure we have enough raw data
        nweeks = int( ndays / 7 )
        ndays  = 7 * nweeks
        nraw   = ndays + 1

        # strip down dates to 1 per week
        weeks = dates[-ndays:].reshape(-1,7)[:,6]

        # add up all counties in state (filtering "non-states")
        for row in reader:
            state = row[6]

            if state not in states.us_state_abbrev: 
                continue

            county = row[5]
            state  = states.us_state_abbrev[state]

            raw = np.array(row[-nraw:],dtype=int)

            daily = raw[1:] - raw[:-1]
            weekly = np.sum(daily.reshape(-1,7),axis=1)

            if state not in state_data:
                state_data[state] = {
                  'total'  : 0,
                  'daily'  : np.zeros(ndays, dtype=int),
                  'weekly' : np.zeros(nweeks, dtype=int),
                  }

            if state not in county_data:
                county_data[state] = dict()

            if county not in county_data[state]:
                county_data[state][county] = {
                  'total' : 0,
                  'daily'  : np.zeros(ndays, dtype=int),
                  'weekly' : np.zeros(nweeks, dtype=int),
                  }

            sd = state_data[state]
            sd['total']  = sd['total'] + raw[-1]
            sd['daily']  = np.add(sd['daily'], daily)
            sd['weekly'] = np.add(sd['weekly'], weekly) 

            cd = county_data[state][county]
            cd['total']  = cd['total'] + raw[-1]
            cd['daily']  = np.add(cd['daily'], daily)
            cd['weekly'] = np.add(cd['weekly'], weekly) 

    data = { 
        'timestamp'  : time.time() ,
        'dates'      : dates,
        'weeks'      : weeks,
        'state'      : state_data,
        'county'     : county_data
        }

    print("Using newly downloaded data from JHU");

    try:
        with open('data/jhu.np',mode='wb') as fp:
            pickle.dump(data,fp)
    except Exception as e:
        print("Exception writing data: " + str(e));
        pass

    return data

