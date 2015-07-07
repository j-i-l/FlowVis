__author__ = 'Jonas I Liechti'
from visualizer import TVis
from matplotlib.colors import cnames
import os
import errno


class Scenario():
    def __init__(
            self, input_path,
            node_parser,
            edge_parser,
            attack_parser,
            solution_parser,
            **kwargs
    ):
        self.path = input_path
        self.load_nodes = node_parser
        self.load_edges = edge_parser
        if attack_parser:
            self.load_attack = attack_parser
        if solution_parser:
            self.load_solution = solution_parser
        self.nodes_file = kwargs.get(
            'nodes_file',
            os.path.join(
                self.path,
                'input',
                'nodes.txt'
            )
        )
        self.edges_file = kwargs.get(
            'edges_file',
            os.path.join(
                self.path,
                'input',
                'edges.txt'
            )
        )
        # initialize the color mapper
        self.color_mapper = {name: hex_code for name, hex_code in cnames.iteritems()}
        colors = kwargs.get('colors', None)
        if colors:
            colors = {k: self.color_mapper.get(k, colors[k]) for k in colors}
            self.tvis = TVis(
                nodes=self.load_nodes(self.nodes_file),
                edges=self.load_edges(self.edges_file),
                colors=colors
            )
        else:
            self.tvis = TVis(
                nodes=self.load_nodes(self.nodes_file),
                edges=self.load_edges(self.edges_file),
            )
        self.attack_file = kwargs.get(
            'attack_file',
            os.path.join(
                self.path,
                'input',
                'attack.txt'
            )
        )
        self.solution_file = kwargs.get(
            'solution_file',
            os.path.join(
                self.path,
                'solution.txt'
            )
        )
        # initialize the configurations
        self.before_config = None
        self.after_config = None

    def visualize(
            self, output_dir, solution_file=None, attack_file=None,
            format='.pdf',
            visualize_solution=True, visualize_attack=False,
            visualize_layout=False, **kwargs
    ):
        """
        Visualizes a scenario
        :param output_dir: Directory where the output files should be created.
        :param solution_file: Path the the solution file
        :param attack_file: Path to the attack file
        :param format: format of the output files (default: .pdf)
        :param visualize_solution: Indicate whether to plot the solution
        :param visualize_attack: Indicate whether to plot just the attack scenario
        :param visualize_layout: Indicate whether to plot the basic layout of the network
        :param kwargs: optional arguments passed to the visualization procedure.
        :return:
        """
        # make sure the output directory exists, if not create it
        try:
            os.makedirs(output_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        if solution_file:
            self.solution_file = solution_file
        if attack_file:
            self.attack_file = attack_file
        if visualize_layout:
            self.tvis.to_visual_elements(**kwargs)
            self.tvis.save_figure(
                os.path.join(
                    output_dir,
                    'basic_layout{}'.format(format)
                )
            )
        if not os.path.isfile(self.attack_file):
            visualize_attack = False
        if not os.path.isfile(self.solution_file):
            visualize_solution = False
        # load the attack scenario
        if any([visualize_attack, visualize_solution]):
            self.tvis.load_attack(*self.load_attack(self.attack_file))
            if visualize_attack:
                self.tvis.to_visual_elements(**kwargs)
                self.tvis.save_figure(
                    os.path.join(
                        output_dir,
                        'attack_plan{}'.format(format)
                    )
                )
            # load the solution configurations
            self.before_config, self.after_config = self.load_solution(self.solution_file)
            # set the status before the attack
            self.tvis.reset_functionality()
            self.tvis.load_config(self.before_config)
            # visualize scenario before attack
            self.tvis.to_visual_elements(**kwargs)
            if visualize_solution:
                self.tvis.save_figure(
                    os.path.join(
                        output_dir,
                        'solution_before{}'.format(format)
                    )
                )
            # load the configuration after the attack
            self.tvis.load_attack(*self.load_attack(self.attack_file))
            self.tvis.load_config(self.after_config)
            #visualize the scenario after the attack
            self.tvis.to_visual_elements(**kwargs)
            if visualize_solution:
                self.tvis.save_figure(
                    os.path.join(
                        output_dir,
                        'solution_after{}'.format(format)
                    )
                )
