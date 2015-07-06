__author__ = 'Jonas I Liechti'
"""
This is a simple usage case of the flowvis package.


"""
# load the custom file parsers (they are quick and dirty)
from file_parsers import *
# load the flowvis package
from flowvis import Scenario
# load the json package to process the config.json file
import json

path = './'
attack_file = 'input/attack_simple.txt'
solution_file = 'solution_simple.txt'

# load the configuration file
with open('config.json', 'r') as f:
    jsondata = f.read()

my_config = json.loads(jsondata)

# get the color form the config.json file, use default setting if no colors are provided
my_colors = my_config.pop(
    'colors',
    {
        'lc': '0.2',  # layoutcolor
        'tc': 'black',  # textcolor
        'ec': '0.25',  # edge_layoutcolor
        'uc': 'blue',  # usercolor'
        'pc': 'yellow',  # producercolor
        'ex': 'orange',  # excesscolor
        'ac': 'red',  # alertcolor
        'wc': 'orange',  # warningcolor
        'bc': 'white'  # _backgroundcolor
    }
)


# initialize the scenario:
simple_scenario = Scenario(
    path,
    load_nodes,
    load_edges,
    load_attack,
    load_solution,
    colors=my_colors
)

simple_scenario.visualize(
    'plots',
    attack_file=attack_file,  # specify the file holding the attack scenario
    solution_file=solution_file,
    **my_config
)
