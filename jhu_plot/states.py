#

import os
import csv

data_dir = os.path.split(__file__)[0] + "/../data"

names = dict()
codes = dict()
with open(f"{data_dir}/us_state_abbrev.csv","r") as file:
    for code,name in csv.reader(file):
        name = name.rstrip().lstrip()
        names[code] = name
        codes[name] = code

us_population = None
state_population = dict()
with open(f"{data_dir}/population.csv","r") as file:
    for row in csv.reader(file):
        name = row[4].lstrip().rstrip()
        pop = row[5]

        if name == "United States":
            us_population = pop
        elif name in codes:
            state_population[codes[name]] = pop

county_populations = dict()
with open(f"{data_dir}/co-est2019-annres.dat") as file:
    for county,state,pop in csv.reader(file,delimiter='|'):
        state = codes[state]
        if state not in county_populations:
            county_populations[state] = {}
        county_populations[state][county] = pop
    

def name(code):
    return names[code]

def code(name):
    return codes[name]

def counties(state):
    if state in codes:
        state = codes[state]
    return list(county_populations[state].keys())

def population(state, county=None):
    if state in codes:
        state = codes[state]
    if county:
        return county_populations[state][county]
    else:
        return state_population[state]
