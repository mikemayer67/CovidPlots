#!/usr/bin/env python

import common.states as states

counties = {}

def load_data():
    if counties:
        return
    with open('data/co-est2019-annres.dat') as fp:
        for line in fp:
            line = line.strip()
            county,state,pop = line.split('|')
            state = states.us_state_abbrev[state]
            if state not in counties.keys():
                counties[state] = {}
            counties[state][county] = int(pop)

def population(county,state):
    load_data()
    if state not in counties.keys():
        print("Missing county data for {}".format(state))
        return 1000000000000
    if county not in counties[state].keys():
        print("Missing county data for {}, {}".format(county,state))
        return 1000000000000
    return counties[state][county]

