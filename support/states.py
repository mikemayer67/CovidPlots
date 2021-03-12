# United States of America Python Dictionary to translate States,
# Districts & Territories to Two-Letter codes and vice versa.
#
# https://gist.github.com/rogerallen/1583593
#
# Dedicated to the public domain.  To the extent possible under law,
# Roger Allen has waived all copyright and related or neighboring
# rights to this code.

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

# thank you to @kinghelix and @trevormarburger for this idea
abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))


# state population data from:
#  https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/state/detail/SCPRC-EST2019-18+POP-RES.csv

us_state_population = {
    'Alabama': 4903185,
    'Alaska': 731545,
    'Arizona': 7278717,
    'Arkansas': 3017804,
    'California': 39512223,
    'Colorado': 5758736,
    'Connecticut': 3565287,
    'Delaware': 973764,
    'District of Columbia': 705749,
    'Florida': 21477737,
    'Georgia': 10617423,
    'Hawaii': 1415872,
    'Idaho': 1787065,
    'Illinois': 12671821,
    'Indiana': 6732219,
    'Iowa': 3155070,
    'Kansas': 2913314,
    'Kentucky': 4467673,
    'Louisiana': 4648794,
    'Maine': 1344212,
    'Maryland': 6045680,
    'Massachusetts': 6892503,
    'Michigan': 9986857,
    'Minnesota': 5639632,
    'Mississippi': 2976149,
    'Missouri': 6137428,
    'Montana': 1068778,
    'Nebraska': 1934408,
    'Nevada': 3080156,
    'New Hampshire': 1359711,
    'New Jersey': 8882190,
    'New Mexico': 2096829,
    'New York': 19453561,
    'North Carolina': 10488084,
    'North Dakota': 762062,
    'Ohio': 11689100,
    'Oklahoma': 3956971,
    'Oregon': 4217737,
    'Pennsylvania': 12801989,
    'Rhode Island': 1059361,
    'South Carolina': 5148714,
    'South Dakota': 884659,
    'Tennessee': 6829174,
    'Texas': 28995881,
    'Utah': 3205958,
    'Vermont': 623989,
    'Virginia': 8535519,
    'Washington': 7614893,
    'West Virginia': 1792147,
    'Wisconsin': 5822434,
    'Wyoming': 578759,
    'Puerto Rico': 3193694
}

abbrev_population = { us_state_abbrev[k]:v for (k,v) in us_state_population.items() }

us_population = sum((v for (_,v) in us_state_population.items()))
