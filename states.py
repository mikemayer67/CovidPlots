#!/usr/bin/env python
"Imports and plots the state confirmed cases"

import numpy as np
import requests
from contextlib import closing
import csv
import matplotlib.pyplot as plt
import time
import math

#url = "http://samplecsvs.s3.amazonaws.com/SalesJan2009.csv"
# url = "https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"

totals = dict()

rq = requests.get(url,stream=True)
with closing(rq) as r:
    f = (line.decode('utf-8') for line in r.iter_lines())
    reader = csv.reader(f, delimiter=',',quotechar='"')
    columns = next(reader)
    dates = np.array(columns[55:])

    zeros = np.zeros(dates.size)

    for row in reader:
        state = row[6]
        counts = np.array(row[55:],dtype=int)
        base = totals.get(state,zeros)
        totals[state] = np.add(totals.get(state,zeros), counts)

ncol = dates.size - 1
ncol = ncol - ncol % 7
weeks = dates[6-ncol::7]
nweeks = len(weeks)

max_weekly = 0

weekly = dict()
total  = dict()
for state,data in totals.items():
    diff = data[1:] - data[:-1]
    diff = diff[-ncol:].reshape(-1,7)
    weekly[state] = np.sum(diff,axis=1)
    total[state] = data[-1]
    t = max(weekly[state])
    if t > max_weekly:
        max_weekly = t

states = [ x[0] for x in sorted(total.items(), key=lambda x: x[1], reverse=True) ]

weekly_sorted = [ weekly[state] for state in states ]

plt.ion()
plt.stackplot(weeks,weekly_sorted)
plt.legend(states,loc='upper left',ncol=2,fontsize='xx-small')
plt.xlabel("Week")
plt.ylabel("Weekly New Cases")
plt.gca().set_title('States Ordered by Total Cases')

input("Press Enter to continue...")

states.reverse()

weekly_sorted = [ weekly[state] for state in states ]

plt.ion()
plt.stackplot(weeks,weekly_sorted)
plt.legend(states,loc='upper left',ncol=2,fontsize='xx-small')
plt.xlabel("Week")
plt.ylabel("Weekly New Cases")
plt.gca().set_title('States Ordered by Total Cases')

input("Press Enter to continue...")

states = [ x[0] for x in sorted(weekly.items(), key=lambda x: x[1][-1], reverse=True) ]

weekly_sorted = [ weekly[state] for state in states ]

plt.gca().set_prop_cycle(None)
plt.stackplot(weeks,weekly_sorted)
plt.legend(states,loc='upper left',ncol=2,fontsize='xx-small')
plt.xlabel("Week")
plt.ylabel("Weekly New Cases")
plt.gca().set_title('States Ordered by Current New Cases')

input("Press Enter to continue...")

states.reverse()

weekly_sorted = [ weekly[state] for state in states ]

plt.gca().set_prop_cycle(None)
plt.stackplot(weeks,weekly_sorted)
plt.legend(states,loc='upper left',ncol=2,fontsize='xx-small')
plt.xlabel("Week")
plt.ylabel("Weekly New Cases")
plt.gca().set_title('States Ordered by Current New Cases')

input("Press Enter to continue...")

ind = np.arange(nweeks)

yy = math.log10(max_weekly)
my = int(yy)
cy = yy - my
sy = 10**my
fy = int(10**(cy+1)+1)/10
y  = list(range(0, int(fy*sy), int(0.5*sy)))

for state in states:
    plt.ion()
    plt.gca().set_prop_cycle(None)
    plt.cla()
    plt.bar(ind, weekly[state], 0.4)
    plt.xticks(ind,weeks)
    plt.yticks(y)
    plt.title(state)
    plt.pause(1.0)





