__author__ = 'Jonas I Liechti'
DESC = """
    Defines the classes of the two structural elements: nodes and edges
"""
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrow
from matplotlib.transforms import Affine2D
from packages.vecpy import Vector as Vec

# gives the color of edges, borders etc
layoutcolor = '0.2'
# give the color for the edges
edge_layoutcolor = '0.25'
# the color of user nodes
usercolor = 'blue'
# the color of producer nodes
producercolor = 'yellow'
# what color should indicate excess of goods
excesscolor = 'orange'
# color indication non-covering of needs
alertcolor = 'red'
# color for warning labels
warningcolor = 'orange'
# the color of the background
_backgroundcolor = 'white'


class Edge():
    def __init__(
            self, start_node, end_node, capacity=None, flux=None,
            unitcost=None, strength=None, functional=True, ID=None, **kwargs
    ):
        """

        :param ID: identifier of the edge (optional
        :param start_node: Node class object from which the edge starts
        :param end_node: Node class object at which the edge ends
        :param capacity: maximal flux capacity [units per time]
        :param flux: effective flux [units per time]. Note if the flux is None,
            it is assumed that we are in layout mode. If there is no flux, set flux to 0
        :param unitcost: cost of transport for an unit
        :param strength:
        :param functional:
        :param kwargs:
        :return:
        """
        self._id = ID
        self.s_node = start_node
        self.e_node = end_node
        self._s_id = self.s_node._id
        self._e_id = self.e_node._id
        self.capacity = capacity
        self.flux = flux
        self.unitcost = unitcost
        self.strength = strength
        self.functional = functional
        self.kwargs = kwargs

    def is_this(self, ids):
        if isinstance(ids, tuple):
            return True if self.s_node.is_this(ids[0]) and self.e_node.is_this(ids[1]) else False
        else:
            return True if self._id == ids else False


class EdgeVis():
    def __init__(self, edge, coords_scaling=((1., 0, 1.), (1., 0, 1.)),
                 **kwargs):

        self.edge = edge
        # determine whether to plot layout mode or not
        if self.edge.flux is None:
            self.layout_mode = True
        else:
            self.layout_mode = False
        # each EdgeVis is a segment of lines. ideally the list contains a single element (straight connection)
        # but this is not mandatory. to avoid drawing NodeVis elements over edges, an edge can be deviated around
        # a node.
        self._coords_scaling = coords_scaling
        self.segments = [
            (self.s_coords, self.e_coords)
        ]
        # set the alpha channel depending on whether the node is functional or not
        if self.functional:
            self.alpha = 1
        else:
            self.alpha = 0.3
        # if one wants to get specific values from the kwargs:
        self.pen_costs = kwargs.get('pens_costs', None)
        self.width_scale = kwargs.get('width_scale', 0.1)
        self.label_scale = kwargs.get('label_scale', 1.)
        self.edge_scale = kwargs.get('edge_scale', 1.)
        self.node_scale = kwargs.get('node_scale', 1.)
        self.scale = kwargs.get('scale', 0.01)
        self.with_label = kwargs.get('with_label', True)
        self.visible = kwargs.get('visible', True)
        self.label_position = kwargs.get('label_position', 0.5)
        self.kwargs = kwargs
        self.patch_collection = []
        self.super_patch_collection = []
        self.non_functional_patch_collection = []
        # initialize the structures
        self.basic_structure = []

    @property
    def functional(self):
        return self.edge.functional

    @property
    def s_coords(self):
        return tuple(map(
            lambda x: round(x, 5),
            self.edge.s_node.coord_scaling(self._coords_scaling)
        ))

    @property
    def e_coords(self):
        return tuple(map(
            lambda x: round(x, 5),
            self.edge.e_node.coord_scaling(self._coords_scaling)
        ))

    @property
    def capacity(self):
        return self.edge.capacity

    def _update(self, colors):
        """
        This method update the graphical elements associated to an edge.
        It should be called whenever an edge is updated.
        :return:
        """
        # determine whether we are in the layout mode or not
        if self.edge.flux is None:
            self.layout_mode = True
        else:
            self.layout_mode = False
        self._basic_outline(colors)
        # create the edge label
        self._label(colors)

    def _basic_outline(self, colors):
        #(xy, width, height, angle=0.0, **kwargs)
        opt = {
            'head_width': 3 * self.width_scale, 'head_length': 6 * self.width_scale, #'width': 0.2,
            'length_includes_head': True, 'shape': 'full'
        }
        nbr_segments = len(self.segments)
        self.basic_structure = []
        for i in xrange(nbr_segments):
            if i == nbr_segments - 1:  # the last part, so we need to draw the arrow head
                opt['head_width'] = 2 * self.width_scale * self.edge_scale
                opt['head_length'] = 6 * self.width_scale * self.node_scale
                opt['length_includes_head'] = True
                #opt['shape'] = 'left'
            else:  # intermediary segment
                opt['head_width'] = 0.5 * self.width_scale
                opt['head_length'] = 0.3 * self.width_scale
                opt['length_includes_head'] = False
                #opt['shape'] = 'left'
            s_coords, e_coords = self.segments[i]
            #print s_coords, e_coords
            base_line = FancyArrow(
                s_coords[0], s_coords[1], e_coords[0] - s_coords[0], e_coords[1] - s_coords[1], fill=True,
                # to do: use fill false for non-functional or use fc and ec (face and edge color
                ec=colors['ec'], fc=str(1 * float(colors['ec'])),
                width=0.5 * self.width_scale * self.edge_scale, alpha=self.alpha,
                **opt
            )
            self.basic_structure.append(base_line)

    def _label(self, colors):
        """
        Method to create an edges label

        :return:
        """

        its_label = '{:g}'.format(abs(self.edge.capacity) if self.edge.capacity is not None else '')
        status_color = colors['bc']
        if not self.layout_mode:
            in_percent = int(round(100 * self.edge.flux / float(self.edge.capacity), 0))
            if in_percent < 100:
                status_color = colors['wc']
            its_label += '; {:g}%'.format(in_percent)
        # get the label coordinates based on self.segments (use the end of the first segment if several segments are
        # present, if it is a single, place the label half the way

        s_coords, e_coords = self.segments[0]
        edge_vec = Vec(s_coords, e_coords)
        start_vec = Vec(s_coords)
        # maybe always use the last part...
        if len(self.segments) == 1:  # single segment: place it half way
            part_way_vec = start_vec + self.label_position * edge_vec
            coords_label = part_way_vec.coords[:2]
        else:  # several segments: place label at the end of the first
            #half_way_vec = start_vec + 0.5 * edge_vec
            #coords_label = half_way_vec.coords[:2]
            coords_label = e_coords
        if self.with_label:
            self.labels = [
                # so far there is just a single label for an edge
                (
                    its_label,
                    coords_label,
                    {
                        'horizontalalignment': 'center',
                        'verticalalignment': 'center',
                        'size': self.scale * 200 * self.label_scale,
                        'color': colors['tc'],
                        'box_fc': status_color
                    }
                )
            ]
        else:
            self.labels = None
        # cross through the label if it is not functional
        if not self.functional:
            cross_bar = FancyBboxPatch(
                (0, 0), self.scale * self.label_scale, 0.07 * self.scale * self.label_scale,
                boxstyle="square,pad={}".format(0.05 * self.scale * self.label_scale),
                color=alertcolor, alpha=min(1, 2 * self.alpha), zorder=6
            )
            rotator = Affine2D().rotate_deg(-45)
            corner_coords = (
                coords_label[0] - 0.4 * self.scale * self.label_scale,
                coords_label[1] + 0.3 * self.scale * self.label_scale
            )
            translator = Affine2D().translate(*corner_coords)
            transform = rotator + translator
            cross_bar.set_transform(transform)
            self.super_patch_collection.append(cross_bar)

    def get_visual_elements(self, colors):
        """
        Simply returns the patch collection of the node
        :return:
        """
        # empty the patch collection
        self.patch_collection = []
        self.super_patch_collection = []
        self._update(colors)
        # show the status if the node has a capacity
        self.patch_collection.extend(self.basic_structure)
        if self.visible:
            return self.patch_collection, self.labels, self.super_patch_collection
        else:
            return None

    def get_label(self):
        # to do: does not call self._update, so the labels might not be up to date
        return self.labels

class Node():
    def __init__(
            self, ID, coords=None, need=None, coverage=None, penalty=None, strength=None, functional=True, **kwargs
    ):
        """
            Creates a new node object for a transport system.

            :param coords: The coordinates of the node
            :type coords: tuple
            :param need: Capacity of the node
            :type need: float, int
            :param coverage: Effective load of the node
            :type coverage: float, int
            :param penalty: Per unit cost of non-covered need
            :type penalty: float, int
            :param functional: Indication if the node is functional or not
            :type functional: bool
            :param kwargs:
            :return:
        """
        self._id = ID
        self.coords = coords
        self.functional = functional
        self.need = need
        self.coverage = coverage
        self.penalty = penalty
        self.strength = strength
        # if one wants to get specific values from the kwargs:
        #self.pen_costs = kwargs.get('pens_costs', None)
        self.total_costs = kwargs.get('total_costs', None)
        self.kwargs = kwargs

    def is_this(self, an_id):
        return True if self._id == an_id else False

    def coord_scaling(self, coords_scaling):
        return (
            coords_scaling[0][1] + coords_scaling[0][0] * (
                self.coords[0] - coords_scaling[0][2]
            ),
            coords_scaling[1][1] + coords_scaling[1][0] * (
                self.coords[1] - coords_scaling[1][2]
            )
        )


class NodeVis():
    def __init__(self, node, r=1, coords_scaling=((1., 0, 1.), (1., 0, 1.)), **kwargs):
        """
            Creates a new node object for a transport system.

            :param r: Reference radius: the node size will not exceed 1.5* this radius
            :type r: float
            :param coords_scaling: factors and offsets by which the coordinates should be scaled
                to fit into to figure canvas.
            :type coords_scaling: tuple, list
            :param kwargs:
            :return:
        """
        self.node = node
        self.r = r
        if self.functional:
            self.alpha = 1
        else:
            self.alpha = 0.3
        # how much smaller should a transit node be
        self._transit_fraction = kwargs.get('transit_fraction', 3.)
        # give the possibility to return normalized coords already
        self._coords = kwargs.get('coords', None)
        self.scale = kwargs.get('scale', 0.1)
        self.node_scale = kwargs.get('node_scale', 1.)
        self.r *= self.node_scale
        self.label_scale = kwargs.get('label_scale', 1.)
        self.with_label = kwargs.get('with_label', False)
        self.show_id = kwargs.get('show_id', False)
        self.kwargs = kwargs
        # initialize an empty patch collection
        self.patch_collection = []
        self.super_patch_collection = []
        self._coords_scaling = coords_scaling
        # determine whether to plot layout mode or not
        if self.node.coverage is None:
            self.layout_mode = True
        else:
            self.layout_mode = False
        # initialize the color for the node's role (call self._update to get it working)
        self.role_color = None
        #self._update()

    # make arguments from the Node class directly accessible
    @property
    def coords(self):
        """
        Retrun the coordinates of the node realtive to the file canvas, i.e. in [0, 1]
        :return:
        """
        if self._coords:
            return self._coords
        else:
            noramlized = self.node.coord_scaling(self._coords_scaling)
            return tuple(map(lambda x: round(x, 5), noramlized))

    @property
    def functional(self):
        return self.node.functional

    @property
    def _id(self):
        return self.node._id

    @property
    def need(self):
        return self.node.need

    @property
    def coverage(self):
        return self.node.coverage

    @property
    def penalty(self):
        return self.node.penalty

    @property
    def strength(self):
        return self.node.strength

    @property
    def functional(self):
        return self.node.functional

    def _update(self, colors):
        """
        This method creates the graphical elements for the node.
        Upon alternation of some of the nodes properties it should be called to
        update graphical object.
        :return:
        """
        # determine whether to plot just the layout or a solution to the flow
        if self.node.coverage is None:
            self.layout_mode = True
        else:
            self.layout_mode = False
        # set the type of node (user/producer)
        if self.need < 0.:
            self.role_color = colors['pc']
        else:
            self.role_color = colors['uc']
        # setup the patch_collection
        self.patch_collection = []
        self.super_patch_collection = []
        # draw background
        self._background(colors)
        # draw the basic structure
        self._basic_outline(colors)
        # draw the status if we are not in layout mode
        if not self.layout_mode:
            self._draw_status(colors)
        # create the node label
        self._label(colors)

    def _background(self, colors):
        background_circle = Circle(
            self.coords,
            self.r if self.need != 0. else self.r / self._transit_fraction,
            color=colors['bc'], zorder=1, fill=True, edgecolor='none', alpha=1
        )
        self.background = [background_circle]

    def _basic_outline(self, colors):
        if self.need != 0:
            #center = Circle(
            #    self.coords,
            #    self.r / float(20),
            #    color=color['lc'], zorder=4, facecolor=color['lc'], fill=True, alpha=self.alpha
            #)
            if self.layout_mode:
                border = Circle(
                    self.coords, 0.99 * self.r, color=colors['lc'], zorder=3, fill=False, edgecolor=colors['lc'],
                    alpha=self.alpha, linewidth=70 * self.scale
                )
                role_fill = Circle(
                    self.coords, self.r, color=self.role_color, zorder=4, facecolor=self.role_color, fill=True,
                    alpha=0.5 * self.alpha
                )
                self.basic_structure = [role_fill, border]
            else:
                border = Circle(
                    self.coords, self.r, color=colors['lc'], zorder=3, fill=False, edgecolor=colors['lc'],
                    alpha=self.alpha, linewidth=0.5
                )
                self.basic_structure = [border, ]#center]
        else:
            center = Circle(
                self.coords, self.r / self._transit_fraction, color=colors['lc'], zorder=4, facecolor=colors['lc'],
                fill=True, alpha=self.alpha
            )
            self.basic_structure = [center]
        if not self.functional:
            size = self.r if self.need != 0. else self.r / self._transit_fraction
            cross_bar = FancyBboxPatch(
                (0, 0), 2.4 * size, 0.2 * size,
                boxstyle="square,pad={}".format(0.05 * self.scale * self.label_scale),
                color=colors['ac'], alpha=min(1, 2 * self.alpha), zorder=6
            )
            rotator = Affine2D().rotate_deg(-40)
            corner_coords = (
                self.coords[0] - size,
                self.coords[1] + 0.7 * size
            )
            translator = Affine2D().translate(*corner_coords)
            transform = rotator + translator
            cross_bar.set_transform(transform)
            self.super_patch_collection.append(cross_bar)

    def _draw_status(self, colors):
        r_status = self.r * (abs(self.coverage / float(self.need))) if self.need != 0.0 else 0
        # this will hold all the circles belonging to status
        self.status = []
        #if self.functional:
        # if there is more than needed
        if r_status > self.r:
            r_status = self.r
            # indicate that the overflow is bigger (3 small circles around
            crit1 = Circle(
                self.coords, 1.05 * self.r, color=colors['ec'], zorder=3, fill=False,
                alpha=0.9 * self.alpha,
                linestyle='solid', linewidth=3
            )
            crit2 = Circle(
                self.coords, 1.15 * self.r, color=colors['ec'], zorder=3, fill=False,
                alpha=0.7 * self.alpha,
                linestyle='solid', linewidth=2
            )
            crit3 = Circle(
                self.coords, 1.21 * self.r, color=colors['ec'], zorder=3, fill=False,
                alpha=0.5 * self.alpha,
                linestyle='solid', linewidth=1
            )
            self.status.append(crit1)
            self.status.append(crit2)
            self.status.append(crit3)
        if r_status < self.r:
            # not enough to cover the need of this node
            status_background = Circle(
                self.coords, self.r, color=colors['ac'], zorder=3, fill=True, edgecolor='none',
                alpha=0.5 * self.alpha
            )
            # crit1 = Circle(
            #     self.coords, 1.05 * r_status, color=colors['ac'], zorder=3, fill=False,
            #     edgecolor=colors['ac'], alpha=self.alpha,
            #     linestyle='solid', linewidth=2
            # )
            # crit2 = Circle(
            #     self.coords, 1.1 * r_status, color=colors['ac'], zorder=3, fill=False,
            #     edgecolor=colors['ac'], alpha=0.9 * self.alpha,
            #     linestyle='solid', linewidth=1
            # )
            # crit3 = Circle(
            #     self.coords, 1.15 * r_status, color=colors['ac'], zorder=3, fill=False,
            #     edgecolor=colors['ac'], alpha=0.6 * self.alpha,
            #     linestyle='dashed', linewidth=0.5
            # )
            self.status.append(status_background)
            #self.status.append(crit1)
            #self.status.append(crit2)
            #self.status.append(crit3)
        status_circle = Circle(
            self.coords, r_status, color=self.role_color, zorder=3, fill=True, edgecolor='none', alpha=self.alpha
        )
        self.status.append(status_circle)

    def _label(self, colors):
        # return None if it is a transit node or no label should be shown
        if self.show_id:
            self.labels = []
            id_label = str(self._id)
            coords_id = (
                self.coords[0],
                self.coords[1]
            )
            self.labels.append(
                (
                    id_label,
                    coords_id,
                    {
                        'horizontalalignment': 'center',
                        'verticalalignment': 'center',
                        'size': self.r * 300 * self.label_scale,
                        'color': colors['tc'],
                        'box': False
                    }
                )
            )
        else:
            self.labels = None
        if self.need == 0.0 or not self.with_label:
            pass
        else:
            its_capacity = '{:g}'.format(abs(self.need))
            cap_pen = its_capacity
            if self.penalty:
                cap_pen += '; {:1g}'.format(self.penalty)
            coords_cap = (
                self.coords[0] + self.r if self.need != 0 else self.coords[0] + (self.r / self._transit_fraction),
                self.coords[1] - self.r if self.need != 0 else self.coords[1] - (self.r / self._transit_fraction)
            )
            coords_coverage = (
                self.coords[0] + self.r,
                self.coords[1] + self.r
            )
            capacity_label = (
                cap_pen,
                coords_cap,
                {
                    'horizontalalignment': 'center',
                    'verticalalignment': 'bottom',
                    'size': 250 * self.r * self.label_scale,
                    'color': colors['tc']
                }
            )
            # show the capacity only in layout mode
            if self.layout_mode:
                self.labels.append(capacity_label)
            #self.labels = [capacity_label] if self.layout_mode else []
            # add info about coverage of the need if it is not a transit node and we are not in layout mode
            if self.need != 0 and not self.layout_mode:
                in_percent = int(abs(self.coverage) / float(abs(self.need)) * 100)
                if in_percent < 100:
                    status_color = colors['ac']
                else:
                    status_color = colors['bc']
                coverage = '{}; {:g}%'.format(
                    its_capacity,
                    in_percent
                )
                self.labels.append(
                    # what the node gets in percent
                    (
                        coverage,
                        coords_coverage,
                        {
                            'horizontalalignment': 'right',
                            'verticalalignment': 'top',
                            'size': self.r * 250 * self.label_scale,
                            'color': colors['tc'],
                            'box_fc': status_color
                        }
                    )
                )
            #ax.annotate('axes center', xy=(.5, .5),  xycoords='axes fraction',
            #        horizontalalignment='right', verticalalignment='bottom')
    def get_visual_elements(self, colors):
        """
        Simply returns the patch collection of the node
        :return:
        """
        # empty the patch collection
        self.patch_collection = []
        self._update(colors)
        # show the status if the node has a capacity
        if self.need != 0:
            if self.layout_mode:
                self.patch_collection.extend(self.background)
                self.patch_collection.extend(self.basic_structure)
            else:
                self.patch_collection.extend(self.background)
                self.patch_collection.extend(self.status)
                self.patch_collection.extend(self.basic_structure)
        else:
            self.patch_collection.extend(self.background)
            self.patch_collection.extend(self.basic_structure)
        return self.patch_collection, self.labels, self.super_patch_collection

    def get_label(self):
        return self.labels
