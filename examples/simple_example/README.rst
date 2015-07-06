A simple use case of the flovwis package
========================================

You can run the example as is simply by running the code below:

.. code-block:: bash

    python simple_example.py

This will create a folder 'plots' containing 4 different visualizations.


config.json
-----------

The content of this file is as follows:

.. code-block:: json

    {
      "colors": {
        "lc": "0.2",
        "tc": "black",
        "ec": "0.25",
        "uc": "blue",
        "pc": "yellow",
        "ex": "orange",
        "ac": "red",
        "wc": "yellow",
        "bc": "white"
      },
      "visualize_layout": true,
      "visualize_attack": true,
      "visualize_solution": true,
      "optimize_layout": true,
      "limit_dist_scale": 1,
      "max_segments": 1,
      "attractor": 10,
      "path_attractor": 22,
      "avg_dist": 0.7,
      "iterations": 1000,
      "minimal_control": true,
      "force_layout_show": false,
      "only_node_labels": false,
      "only_edge_labels": false,
      "node_scale": 1.5,
      "edge_scale": 1,
      "label_scale": 1,
      "edge_label_scale": 1.5,
      "node_label_scale": 1,
      "show_node_labels": true,
      "show_edge_labels": true,
      "show_edges": true,
      "with_node_ids": true
    }


file_parser.py
--------------

The file_parser module should contain the functions capable to parse the content of the various input files.
Given that it is likely that the structure of the input files will change, this module is intended to be adapted by the
user so to correctly parse the data from the file. For more details about the structure of the parsed data have a look
at each function in file_parser.py.

Note that

.. code-block:: python

    load_nodes(nodes_file)

and

.. code-block:: python

    load_edges(edges_file)

are the two functions that need to be defined to at least plot the basic layout of the network. If an attack
scenario and the solutions should be visualized as well, then the following two functions need to be defined:

.. code-block:: python

    load_attack(attack_file)
    load_solution(solution_file)


