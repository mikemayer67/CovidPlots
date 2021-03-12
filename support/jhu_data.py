"""
Collection of functions for managing the data from JHU (Johns Hopkins)

This file can be imported and contains the following functions:

    * get_data:  Return JHU data
"""

import csv
import numpy as np
import pickle
import re
import requests
import support.counties as counties
import support.states as states
import time

from contextlib import closing

class IncorrectURL(Exception):
    pass

class JHUData(dict):
    def __init__(self,max_age=None):
        data = cached_data(max_age)

        if data == None:
            data = { k : download_data(k) for k in ['deaths','confirmed'] }
            cache_data(data)

        for k,v in data.items():
            self[k] = v

    def __getattr__(self,k):
        if hasattr(self,k):
            return self[k]
        else:
            return None

    def get_state_data(self,
                       state,
                       data_type='confirmed',
                       frequency=None,
                       smooth=None,
                       yscale=None):
        if isinstance(data_type,list):
            rval = dict()
            for dt in data_type:
                rval[dt] = self.get_state_data(
                    state, data_type=dt, frequency=frequency, smooth=smooth, yscale=yscale)

        else:
            rval = self[data_type]
            if frequency=='daily':
                rval = rval.daily.state[state]
            elif frequency=='weekly':
                rval = rval.weekly.state[state]
            else:
                rval = rval.raw.state[state]

            if smooth and smooth>1:
                c = np.ones(smooth)/smooth
                rval = np.convolve(rval, c, mode='valid')

            if yscale == 'per_capita':
                pop = states.abbrev_population[state]
                rval /= pop

        return rval

    def get_state_current_total(self,state):
        return self['confirmed'].raw.state[state][-1]

    def get_county_data(self,
                        state,
                        data_type='confirmed',
                        frequency=None,
                        smooth=None,
                        yscale=None):
        is_list = isinstance(data_type,list)

        if not is_list:
            data_type = [data_type]

        rval = dict()

        for dt in data_type:
            if frequency=='daily':
                cd = self[dt].daily.county[state]
            elif frequency=='weekly':
                cd = self[dt].weekly.county[state]
            else:
                cd = self[dt].raw.county[state]

            for county,data in cd.items():
                if re.match('^Out of',county) or county == 'Unassigned':
                    continue

                if smooth and smooth>1:
                    c = np.ones(smooth)/smooth
                    data = np.convolve(data, c, mode='valid')

                if yscale == 'per_capita':
                    pop = counties.population(county,state)
                    data /= pop

                if county in rval.keys():
                    rval[county][dt] = data
                elif is_list:
                    rval[county] = dict()
                    rval[county][dt] = data
                else:
                    rval[county] = data

        return rval

    def get_dates(self, 
                  data_type='confirmed',
                  frequency=None,
                  smooth=None):

        if isinstance(data_type,list):
            rval = dict()
            for dt in data_type:
                rval[dt] = self.get_dates(
                    data_type=dt, frequency=frequency, smooth=smooth)

        else:
            if frequency=='daily':
                rval = self[data_type].dates[1:]
            elif frequency=='weekly':
                rval = self[data_type].weeks
            else:
                rval = self[data_type].dates

            if smooth and smooth>1:
                rval = rval[smooth-1:]

        return rval



class StateData(dict):
    def add(self,state, data):
        if state not in self.keys():
            self[state] = data
        else:
            self[state] = np.add(self[state],data)

class CountyData(dict):
    def add(self,state,county,data):
        if state not in self.keys():
            self[state] = dict()
        self[state][county] = data

class RegionalData:
    def __init__(self):
        self.state  = StateData()
        self.county = CountyData()

class DataSet:
    def __init__(self,dates):
        ndays  = dates.size - 1
        nweeks = int(ndays/7)

        self.dates  = dates
        self.weeks  = dates[-7*nweeks + 6 : : 7]

        self.raw    = RegionalData()
        self.daily  = RegionalData()
        self.weekly = RegionalData()

def cached_data(max_age):
    now = time.time()
    try:
        data = pickle.load(open('data/jhu.np','rb'))
        ts = data['timestamp']
        if now < ts + max_age:
            print("Using cached data from JHU downloaded at " + time.ctime(ts))
        else:
            data = None
    except Exception as x:
        data = None

    return data

def cache_data(data):
    try:
        data['timestamp'] = time.time()
        pickle.dump(data,open('data/jhu.np','wb'))
        print("Data cached to data/jhu.np for future use")
    except:
        print("Failed to cache data for future use")
        pass


def download_data(data_type):

    url = '/'.join( ['https://raw.githubusercontent.com',
                     'CSSEGISandData',
                     'COVID-19',
                     'master',
                     'csse_covid_19_data',
                     'csse_covid_19_time_series',
                     '_'.join([ 'time_series_covid19',data_type,'US.csv'])
                    ])

    rq = requests.get(url,stream=True)

    if rq.status_code != 200:
        raise IncorrectURL(url)

    with closing(rq) as r:
        f = ( line.decode('utf-8') for line in r.iter_lines() )
        reader = csv.reader(f, delimiter=',',quotechar='"')
        columns = next(reader)
        dates = np.array(columns[56:])  # skip roughly first 2 months of data

        nraw   = dates.size
        ndays  = dates.size - 1
        nweeks = int(ndays/7)

        data = DataSet(dates)

        for row in reader:
            if row[7] != 'US':
                continue

            state = row[6]
            if state not in states.us_state_abbrev: 
                continue

            state  = states.us_state_abbrev[state]
            county = row[5]

            raw   = np.array(row[-nraw:],dtype=int)
            daily = raw[1:] - raw[:-1]

            weekly = raw[-1-7*nweeks::7]
            weekly = weekly[1:] - weekly[:-1]

            data.raw.state.add(state,raw)
            data.raw.county.add(state,county,raw)

            data.daily.state.add(state,daily)
            data.daily.county.add(state,county,daily)

            data.weekly.state.add(state,weekly)
            data.weekly.county.add(state,county,weekly)

    print("Using newly downloaded " + data_type + " data from JHU");

    return data

