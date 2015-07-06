__author__ = 'Jonas I Liechti'


def load_nodes(nodes_file):
    """
        Function to read out a node file.

        You might want to adapt this method to your needs, depending on the input file.

    :param nodes_file: absolute path to the file containing the nodes configuration
    :return: a list of nodes. Each node is a dict you can use to init a Node object.
    """
    with open(nodes_file, 'r') as f:
        file_content = f.read()
    # split the content in lines and each line in tab separated columns
    file_content = map(lambda x: x.split('\t'), file_content.split('\n'))
    # check if the format is right
    nodes_header = file_content.pop(0)
    nodes = []
    for node_line in file_content:
        if len(node_line) > 1:
            # print node_line
            a_node = {
                'ID': int(node_line[0]),
                'coords': (float(node_line[1]), float(node_line[2])),
                'need': float(node_line[3]),
                'penalty': float(node_line[4]),
                'strength': float(node_line[5]),
            }
            # add the rest of the content
            for i in xrange(6, len(nodes_header)):
                a_node[nodes_header[i]] = node_line[i]
            nodes.append(a_node)
    return nodes


def load_edges(edges_file):
    """
        Quick and dirty function to pares information on edges from a file.

    :param edges_file:
    :return: List of edges. Each edge is a dict, specifying the attributes that should be passed
        to flowvis.visualizer.Edge class.
    """
    edges = []
    with open(edges_file, 'r') as f:
        file_content = f.read()
    # split the content in lines and each line in tab separated columns
    file_content = map(lambda x: x.split('\t'), file_content.split('\n'))
    # check if the format is right
    edge_header = file_content.pop(0)
    for i in xrange(len(file_content)):
        edge_line = file_content[i]
        if len(edge_line) > 1:
            an_edge = {
                'ID': id,
                'start_id': int(edge_line[0]),
                'stop_id': int(edge_line[1]),
                'capacity': float(edge_line[2]),
                'unitcost': float(edge_line[3]),
                'strength': float(edge_line[4]),
                'flux': None,
                }
            an_edge.update(
                **{edge_header[j]: edge_line[j] for j in xrange(6, len(edge_header))}
            )
            edges.append(an_edge)
    return edges


def load_attack(attack_file):
    attacked_nodes = []
    attacked_edges = []
    elements = [attacked_nodes, attacked_edges]
    with open(attack_file, 'r') as f:
        content = [line.split('\t') for line in f.read().split('\r\n')]
    while [' '] in content:
        content.remove([' '])
    while [''] in content:
        content.remove([''])
    which = None
    for line in content:
        if 'Table 1' in line[0]:
            which = 0
        elif 'Table 2' in line[0]:
            which = 1
        else:
            if which == 0:
                elements[which].append(int(line[0]))
            else:
                elements[which].append((int(line[0]), int(line[1])))
    return attacked_nodes, attacked_edges


def load_solution(solution_file):
    before_config = [{}, {}]
    after_config = [{}, {}]
    with open(solution_file, 'r') as f:
        content = [line.split('\t') for line in f.read().split('\r\n')]
    while [' '] in content:
        content.remove([' '])
    while [''] in content:
        content.remove([''])
    # keep track of which table we are reading
    which = None
    for line in content:
        if 'Table 1' in line[0]:
            which = 0
        elif 'Table 2' in line[0]:
            which = 1
        elif 'Table 3' in line[0]:
            which = 2
        else:
            if which == 0:  # we are at the summary
                # To Do: Information on total cost, etc. are not used so far.
                parts = line[0].split()
                attack_loss, normal_costs, attack_costs = float(parts[5]), float(parts[7]), float(parts[9])
                # re.findall(
                #'Total cost of the attack: (\d+.\d+|\d+)  (= (\d+.\d+|\d+) - (\d+.\d+|\d+) ) ',
                #line[0]
                #)[0]
            elif which == 1:  # edge flows before the attack
                if 'covered' not in line[0]:  # we are not at the end of the table
                    start_id, stop_id, flow = int(line[0]), int(line[1]), float(line[2])
                    before_config[1][(start_id, stop_id)] = flow
                else:
                    if 'uncovered' in line[0]:  # there are uncovered needs
                        which = 3
                    else:  # no uncovered needs
                        pass
            elif which == 2:  # edge flow after attack
                if 'covered' not in line[0]:  # we are not at the end of the table
                    start_id, stop_id, flow = int(line[0]), int(line[1]), float(line[2])
                    after_config[1][(start_id, stop_id)] = flow
                else:
                    if 'uncovered' in line[0]:
                        which = 4
            elif which == 3:  # uncovered demands in normal scenario
                before_config[0][int(line[0])] = (float(line[1]), float(line[2]))
            elif which == 4:  # uncovered demand after attack
                print line
                after_config[0][int(line[0])] = (float(line[1]), float(line[2]))
    return before_config, after_config