__author__ = 'Jonas I Liechti'
DESC = """

"""
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
from structure import *


class TVis():
    def __init__(self, nodes, edges, **kwargs):
        """
        :param nodes: a list of nodes. Each node has to be a dict that is passed to the Node class
        :param edges: a list of edges. Each edge is a dict holding among other thins the 'start_id' and 'stop_id'
            that are the ids of the involved nodes
        :param kwargs:
        :return:
        """
        if isinstance(nodes, (list, tuple)):
            self._load_nodes(nodes)
        else:
            raise AttributeError('Invalid argument for nodes_list')
        if isinstance(edges, (list, tuple)):
            self._load_edges(edges)
        else:
            raise AttributeError('Invalid argument for edges_list')
        # determine appropriate size of a node
        self.node_size = 0.1 / round(len(self.nodes) ** 0.5, 0)
        self.top_right_border = kwargs.get('top_right_border', 1 - 2 * self.node_size)
        self.bottom_left_border = kwargs.get('bottom_left_border', 2 * self.node_size)
        self._scaling()
        self.nodes_visualisations = []
        self.edges_visualisations = []
        self.before_config = [{}, {}]  # configuration before the attack
        self.after_config = [{}, {}]  # configuration after attack
        self._colors = {
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
        # get colors, use default if not provided.
        self.colors = kwargs.get('colors', self._colors)
        # log is only used if self._debug_mode is set to true
        self.log = {}
        self._debug_mode = kwargs.get('debug_mode', False)

    def _scaling(self):
        """
        Compute the parameters for the rescaling function.
        The rescaling is realised such that the minimal value along a coordinate will
        be displayed at an offset equal to self.bottom_left border, the maximal value at
        self.top_right_border.
        :return:
        """
        # get max and min of coordinates
        self.x_max = max(map(lambda x: x.coords[0], self.nodes))
        self.x_min = min(map(lambda x: x.coords[0], self.nodes))
        self.x_diff = float(self.x_max - self.x_min)
        self.y_max = max(map(lambda x: x.coords[1], self.nodes))
        self.y_min = min(map(lambda x: x.coords[1], self.nodes))
        self.y_diff = float(self.y_max - self.y_min)
        # compute the scaling factor to obtain relative coordinates
        self.coords_scaling = (
            (
                (self.top_right_border - self.bottom_left_border) / self.x_diff,
                self.bottom_left_border,
                self.x_min
            ),
            (
                (self.top_right_border - self.bottom_left_border) / self.y_diff,
                self.bottom_left_border,
                self.y_min
            )
        )

    def _load_nodes(self, nodes_list):
        """
        Method to import the network structure from a file

        :param nodes_list:
        :type nodes_list: list
        :return:
        """
        self.nodes = []
        print nodes_list
        for a_node in nodes_list:
            self.nodes.append(
                Node(
                    **a_node
                )
            )

    def _load_edges(self, edges_list):
        self.edges = []
        for an_edge in edges_list:
            start_node = self.get_node(an_edge.pop('start_id'))
            stop_node = self.get_node(an_edge.pop('stop_id'))
            self.edges.append(
                Edge(
                    start_node, stop_node,
                    **an_edge
                )
            )

    def get_node(self, an_id):
        for node in self.nodes:
            if node.is_this(an_id):
                return node

    def get_edge(self, ids):
        """
        return the edge matching the id.
        You can either pass an int as argument on a tuple.
        :param ids:
        :return:
        """
        for edge in self.edges:
            if edge.is_this(ids):
                return edge

    def load_attack(self, attacked_nodes, attacked_edges):
        """

        :param attacked_nodes:
        :param attacked_edges:
        :return:
        """
        unf_nodes = [self.get_node(an_id) for an_id in attacked_nodes]
        print unf_nodes
        #filter(lambda x: x._id in attacked_nodes, self.nodes)
        unf_edges = [self.get_edge(an_id) for an_id in attacked_edges]
        #unf_edges = []
        #for edge in self.edges:
        #    for a_edge in attacked_edges:
        #        if edge._s_id in a_edge and edge._e_id in a_edge:
        #            unf_edges.append(edge)
        for node in unf_nodes:
            node.functional = False
        for edge in unf_edges:
            edge.functional = False

    def reset_functionality(self):
        """
        Resets all nodes as edges to functional state.
        :return:
        """
        for node in self.nodes:
            node.functional = True
        for edge in self.edges:
            edge.functional = True

    def load_config(self, configuration):
        """
        Update the visual elements to the set state.

        :param configuration: List containing two dict, one for the nodes and ond for the edges
        :return:
        """
        # set default total coverage, no total costs
        for node in self.nodes:
            node.coverage = node.need
            node.total_costs = None
        # load the configuration
        for node_id in configuration[0]:
            node = self.get_node(node_id)
            node.coverage = node.need - configuration[0][node_id][0]
            node.total_costs = configuration[0][node_id][1]
        # set default no flux
        for edge in self.edges:
            edge.flux = 0.
        # load the configuration
        for edge_id in configuration[1]:
            edge = self.get_edge(edge_id)
            edge.flux = configuration[1][edge_id]

    def to_visual_elements(
            self,
            label_scale=1, node_scale=1, edge_scale=1,
            optimize_layout=True,
            max_segments=2, attractor=16, path_attractor=100, avg_dist=1, iterations=1000,
            **kwargs
    ):
        """
        Method to convert Node and Edge objects to NodeVis and EdgeVis objects for
            plotting and sets the positions for nodes and edges.
        :param label_scale:
        :param node_scale:
        :param edge_scale:
        :param optimize_layout:
        :param max_segments:
        :param attractor:
        :param path_attractor:
        :param avg_dist:
        :param iterations:
        :param kwargs:
        :return:
        """
        edge_label_scale = kwargs.get('edge_label_scale', label_scale)
        node_label_scale = kwargs.get('node_label_scale', label_scale)
        s_n_l = kwargs.get('show_node_labels', True)
        s_e_l = kwargs.get('show_edge_labels', True)
        force_layout_show = kwargs.get('force_layout_show', False)
        if force_layout_show:
            self._debug_mode = True
            import networkx as nx
        show_edges = kwargs.get('show_edges', True)
        with_node_ids = kwargs.get('with_node_ids', False)
        limit_dist_scale = kwargs.get('limit_dist_scale', 1)
        limit_dist = limit_dist_scale * 1.5 * self.node_size
        minimal_control = kwargs.get('minimal_control', True)
        label_position = kwargs.get('edge_label_position', 0.5)
        self._scaling()
        # run through the edges
        self.edges_visualisations = []
        for edge in self.edges:
            self.edges_visualisations.append(
                EdgeVis(
                    edge, coords_scaling=self.coords_scaling,
                    scale=self.node_size, width_scale=0.2 * self.node_size,
                    label_scale=edge_label_scale, edge_scale=edge_scale, node_scale=node_scale,
                    with_label=s_e_l, visible=show_edges, label_position=label_position
                )
            )
        # run through the nodes
        self.nodes_visualisations = []
        for node in self.nodes:
            # create the visual object
            self.nodes_visualisations.append(
                NodeVis(
                    node, r=self.node_size,
                    scale=self.node_size, label_scale=node_label_scale, node_scale=node_scale,
                    coords_scaling=self.coords_scaling,
                    with_label=s_n_l, show_id=with_node_ids
                )
            )
        # get a list of all points to avoid
        checkpoints = [n_vis.coords for n_vis in self.nodes_visualisations]
        # enter the optimization procedure
        if optimize_layout:
            from packages.vecpy import Vector as Vec
            import networkx as nx
            # for every segment if every edge, track id of start and stop points
            endpoint_ids = []
            for edgevis in self.edges_visualisations:
                endpoint_ids.append(
                    [(checkpoints.index(edgevis.segments[0][0]), checkpoints.index(edgevis.segments[0][1]))]
                )

            # list of ids with fixed nodes
            fixed_nodes = range(len(checkpoints))
            nbr_fixed_nodes = len(fixed_nodes)
            # create an network with those points (fixed nodes, no edges)
            layout_graph = nx.Graph()
            for k in xrange(len(checkpoints)):
                layout_graph.add_node(k, pos=checkpoints[k])
                for j in xrange(k):
                    layout_graph.add_edge(j, k, weight=attractor)
            # start the optimization loop
            cycles = 0
            while True:
                # for each edge track the ids of its newly added waypoints
                waypoint_ids = []
                for edgevis in self.edges_visualisations:
                    segment_waypoints = [None for _ in edgevis.segments]
                    waypoint_ids.append(segment_waypoints)
                added_waypoints = False  # keeps track whether improvements are needed
                #  run through the list of real edges
                for e in xrange(len(self.edges_visualisations)):
                    # test whether an segment of the edge comes to close to a node
                    done = False  # indicating if we are done with a segment (are done as soon as single waypoint is added)
                    for f in xrange(len(self.edges_visualisations[e].segments)):
                        s_coords, e_coords = self.edges_visualisations[e].segments[f]
                        seg_vec = Vec(s_coords, e_coords)
                        start_vec = Vec(s_coords)
                        for i in xrange(len(checkpoints)):
                            checkpoint = checkpoints[i]
                            # should not be the start or end point of the segment
                            if i not in endpoint_ids[e][f]:
                                start_point_vec = Vec(s_coords, checkpoint)
                                ortho = seg_vec.proj(start_point_vec) - start_point_vec
                                # if so, split the edge (add a waypoint)
                                if ortho.length <= limit_dist:
                                    # add the waypoint to the checkpoint list and the graph (as movable node)
                                    proj_scale = round(seg_vec.proj(start_point_vec, True), 5)
                                    limit_val = seg_vec.length * proj_scale
                                    if 0 - limit_dist <= limit_val <= seg_vec.length + limit_dist:
                                        # only consider case if the point was not added this round
                                        if all([i not in new_wp_id for new_wp_id in waypoint_ids]):
                                            # we need to add a waypoint
                                            added_waypoints = True
                                            new_waypoint = start_vec + proj_scale * seg_vec
                                            checkpoints.append(
                                                tuple(map(lambda x: round(x, 5), new_waypoint.coords[:2]))
                                            )
                                            new_id = len(checkpoints) - 1
                                            old_endpoints = endpoint_ids[e][f]
                                            if old_endpoints in layout_graph.edges():
                                                layout_graph.remove_edge(*old_endpoints)
                                            if old_endpoints[::-1] in layout_graph.edges():
                                                layout_graph.remove_edge(*old_endpoints[::-1])
                                            endpoint_ids[e][f] = (
                                                old_endpoints[0],
                                                new_id
                                            )
                                            endpoint_ids[e].insert(f + 1, (
                                                new_id,
                                                old_endpoints[1]
                                            ))
                                            #print endpoint_ids
                                            # add it to the waypoint_ids
                                            waypoint_ids[e][f] = new_id
                                            #layout_graph.add_node(new_id, pos=checkpoints[-1], fixed=False)
                                            ## add the edge between close node andd from and to the waypoint as links in the network
                                            if i not in layout_graph.nodes() and i < nbr_fixed_nodes:
                                                #print 'adding', i
                                                layout_graph.add_node(i)
                                                #print 'adding new', new_id
                                                layout_graph.add_node(new_id)
                                                layout_graph.add_edge(i, new_id,
                                                                      weight=attractor)  # add virtual edge between waypoint and the node to avoid
                                            if not minimal_control:  # add a virtual edge to each fixed node
                                                for ci in fixed_nodes:
                                                    if ci != i:
                                                        weight = attractor
                                                        layout_graph.add_edge(ci, new_id, weight=weight)
                                            # how many segments do we have now
                                            nbr_segs = len(endpoint_ids[e])
                                            for segment_ids in endpoint_ids[e]:
                                                start_id, stop_id = segment_ids
                                                if start_id not in layout_graph.nodes():
                                                    layout_graph.add_node(start_id)
                                                if stop_id not in layout_graph.nodes():
                                                    layout_graph.add_node(stop_id)
                                                layout_graph.add_edge(start_id, stop_id, weight=path_attractor)
                                                if start_id < nbr_fixed_nodes or stop_id < nbr_fixed_nodes:
                                                    new_weight = path_attractor
                                                else:
                                                    new_weight = path_attractor
                                                try:
                                                    layout_graph[start_id][stop_id]['weight'] = (nbr_segs - 1) * new_weight
                                                except KeyError:
                                                    layout_graph[stop_id][start_id]['weight'] = (nbr_segs - 1) * new_weight
                                            # add edges between start-waypoint and waypoint-end
                                            #start_id = checkpoints.index(s_coords)
                                            #end_id = checkpoints.index(e_coords)
                                            #layout_graph.add_edge(start_id, i, weight=10)
                                            #layout_graph.add_edge(i, end_id, weight=10)
                                            # done for this edge
                                            done = True
                                            break  # leave the inner for
                        if done:
                            break
                # if no waypoints needed to be added, stop the optimization
                if not added_waypoints:
                    break
                # if points are added run the force layout
                positions = {i: checkpoints[i] for i in xrange(len(checkpoints))}
                #print 'nodes', layout_graph.nodes()
                #print 'edges', layout_graph.edges()
                #print fixed_nodes
                new_positions = nx.spring_layout(
                    layout_graph, dim=2, k=avg_dist,  # * 1 / float(len(layout_graph)) ** 0.5,
                    scale=0.95,
                    pos=positions, fixed=set(fixed_nodes).intersection(layout_graph.nodes()), weight='weight',
                    iterations=iterations
                )
                for _id in range(nbr_fixed_nodes, len(checkpoints)):
                    checkpoints[_id] = tuple(map(lambda x: round(x, 5), list(new_positions[_id])))
                if self._debug_mode:
                    self.log['positions'] = {_id: checkpoints[_id] for _id in layout_graph.nodes()}
                    self.log['layout_network'] = layout_graph
                # update the segments for each edgevis
                while True:
                    rerun = False
                    for e in xrange(len(self.edges_visualisations)):
                        for f in xrange(len(self.edges_visualisations[e].segments)):
                            #print endpoint_ids[e][f], nbr_fixed_nodes
                            if any([_id >= nbr_fixed_nodes for _id in endpoint_ids[e][f]]):
                                # if this for loop is entered then there are waypoints to be added
                                waypoint_id = waypoint_ids[e][f]
                                #print 'new_wp', waypoint_id
                                old_s, old_e = self.edges_visualisations[e].segments[f]
                                # update the coordinates of existing mobile elements
                                if endpoint_ids[e][f][0] >= nbr_fixed_nodes and endpoint_ids[e][f][0] != waypoint_id:
                                    old_s = checkpoints[endpoint_ids[e][f][0]]
                                if endpoint_ids[e][f][1] >= nbr_fixed_nodes and endpoint_ids[e][f][1] != waypoint_id:
                                    old_e = checkpoints[endpoint_ids[e][f][1]]
                                self.edges_visualisations[e].segments[f] = (old_s, old_e)
                                # if a new mobile segment is added, also update
                                if waypoint_id is not None:
                                    self.edges_visualisations[e].segments[f] = (
                                        old_s,
                                        checkpoints[waypoint_id]
                                    )
                                    self.edges_visualisations[e].segments.insert(
                                        f + 1, (
                                            checkpoints[waypoint_id],
                                            old_e
                                        )
                                    )
                                    waypoint_ids[e][f] = None
                                    waypoint_ids[e].insert(f + 1, None)
                                    rerun = True
                                    break
                        if rerun:
                            break
                    if not rerun:
                        break
                #   continue in the loop
                #print checkpoints
                cycles += 1
                if cycles == max_segments:
                    break
        self.create_figure()
        return None

    def _create_figure(self, x_size=10):
        self.fig_1 = plt.figure(figsize=(x_size, (self.x_diff / self.y_diff) * x_size))
        self.ax_1 = plt.subplot(aspect='equal')
        self.ax_1.axis('off')

    def _populate_figure(self):
        # collect all the patches
        patches = []
        # collect all the labels
        labels = []
        # what needs to be drawn over eveything else
        super_patches = []
        # for the box around labels
        bbox_props = dict(
            boxstyle="round", fc=self.colors['bc'],
            ec=self.colors['tc'], alpha=0.8
        )
        # below is going to go into visualizer function
        # first draw the edges
        for edgevis in self.edges_visualisations:
            # draw the edges and label them
            visual_els = edgevis.get_visual_elements(self.colors)
            if visual_els is not None:
                patches.extend(visual_els[0])
                labels.append(visual_els[1])
                super_patches.extend(visual_els[2])
        # now draw the nodes
        for nodevis in self.nodes_visualisations:
            # a node is an object of the TN class
            visual_els = nodevis.get_visual_elements(self.colors)
            patches.extend(visual_els[0])
            labels.append(visual_els[1])
            super_patches.extend(visual_els[2])
        for single_labels in labels:
            # print single_labels
            if single_labels is not None:
                for a_label in single_labels:
                    box_fc = a_label[2].pop('box_fc', self.colors['bc'])
                    with_box = a_label[2].pop('box', True)
                    if not with_box:
                        bbox_props['fc'] = 'none'
                        bbox_props['ec'] = 'none'
                    else:
                        bbox_props['fc'] = box_fc
                        bbox_props['ec'] = self.colors['tc']
                    self.ax_1.annotate(*a_label[:2], bbox=bbox_props, **a_label[2])

        # rotate the red bars
        self.collection = PatchCollection(patches, match_original=True)
        # to do: adjust the size of the annotation text (eg. one size from 0-10, 10-100, 100-1000 nodes
        self.ax_1.add_collection(self.collection)
        if super_patches:
            self.super_collection = PatchCollection(super_patches, match_original=True)
            self.ax_1.add_collection(self.super_collection)
        if self._debug_mode:  # add the network to create the layout on top.
            import networkx as nx
            nx.draw(self.log['layout_network'], self.log['positions'], self.ax_1)

    def _clear_figure(self):
        self.ax_1.cla()
        self.fig_1.clf()

    def create_figure(self):
        self._create_figure()
        self._populate_figure()

    def save_figure(self, filename, path_to_folder='', format='pdf'):
        self.fig_1.tight_layout()
        if '.' in filename:
            filename, format = filename.split('.')
        self.fig_1.savefig(
            '{}{}.{}'.format(path_to_folder, filename, format)
        )

    def show_figure(self):
        plt.show()
        self.fig_1.show()
