__author__ = 'Jonas I Liechti'
"""
This is a simple usage case of the flowvis package.


"""
# load the custom file parsers (they are quick and dirty)
from file_parsers import *
from flowvis import Scenario

path = './'
attack_file = 'input/attack_simple.txt'
solution_file = 'solution_simple.txt'

my_colors = {
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


# initialize the scenario:
simple_scenario = Scenario(
    path,
    load_nodes,
    load_edges,
    load_attack,
    load_solution
)

simple_scenario.visualize(
    'plots',
    attack_file=attack_file,  # specify the file holding the attack scenario
    solution_file=solution_file,
    colors=my_colors,
    visualize_layout=True,
    visualize_attack=True,
    visualize_solution=True,
    # pass on argument for the visualization
    optimize_layout=True,
    limit_dist_scale=1,
    max_segments=1,
    attractor=10,
    path_attractor=22,
    avg_dist=0.7,
    iterations=1000,
    minimal_control=True,
    force_layout_show=False,
    only_node_labels=False,
    only_edge_labels=False,
    node_scale=1.5,
    edge_scale=1,
    label_scale=1,
    edge_label_scale=1.5,
    node_label_scale=1,
    show_node_labels=True,
    show_edge_labels=True,
)