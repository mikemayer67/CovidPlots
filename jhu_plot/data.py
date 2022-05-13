import os
import csv
import time
import requests
import numpy as np
import pickle

from contextlib import closing

from .states import codes as state_codes

data_dir = os.path.split(__file__)[0] + "/../data"

class JHUData:
    def __init__(self,max_age=3600):
        cache_file = f"{data_dir}/cached_data.dtb"
        try:
            data = pickle.load(open(cache_file,"rb"))
            data_time = data['timestamp']
            if time.time() < data_time + max_age:
                self.cases = data.cases
                self.deaths = data.deaths
                print(f"Using cached JHU data from {time.ctime(data_time)}")
                return
        except FileNotFoundError:
            pass

        self.cases = load_data('cases')
        self.deaths = load_data('deaths')

        try:
            data = {
                'timestamp': time.time(),
                'cases':self.cases,
                'deaths':self.deaths,
            }
            pickle.dump(data,open(cache_file,"wb"))
            print(f"Data cached to {cache_file}")
        except Exception as e:
            print("Failed to cache data to {cache_file}: {e}")

class DataSet:
    def __init__(self,data_rows):

        columns = next(data_rows)

        nweeks = (len(columns)-11)//7 - 7 # skip header data and first 7 weeks
        self.dates = np.array(columns[-7*nweeks::7])

        self.county = dict()
        for row in data_rows:
            county, state, country = row[5:8]
            if country == 'US' and state in state_codes:
                state = state_codes[state]
                if state not in self.county:
                    self.county[state] = dict()

                # add weekly totals to state/county data
                self.county[state][county] = np.array(row[-1-7*nweeks::7],dtype=np.int)

        import pdb; pdb.set_trace()
        self.state = dict()

        for state,counties in self.county.items():
            self.state[state] = sum(counties.values())


def load_data(data_type):
    if data_type == 'cases':
        data_type = 'confirmed'

    url = '/'.join( ['https://raw.githubusercontent.com',
                     'CSSEGISandData',
                     'COVID-19',
                     'master',
                     'csse_covid_19_data',
                     'csse_covid_19_time_series',
                     f"time_series_covid19_{data_type}_US.csv"
                    ])

    print(f"Loading {data_type} data from JHU:\n  {url}")

    request = requests.get(url,stream=True)
    assert request.status_code == 200, (
        f"Failed to get data: {request.reason}\n url: {url}" )

    with closing(request) as r:
        f = ( line.decode('utf-8') for line in r.iter_lines() )
        reader = csv.reader(f, delimiter=',',quotechar='"')

        return DataSet(reader)
