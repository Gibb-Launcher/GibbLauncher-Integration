import math
import networkx as nx
import numpy as np

DIREITA = 1
ESQUERDA = 0
CIMA = 1
BAIXO = 0

class Candidate():
    def __init__(self, data, noise=True):
        self.data = data
        self.noise = noise


def create_graph(data):
    graph = nx.DiGraph()
    for index, item in data.items():
        detect_neighbor(index, item, data, graph)

    return graph


def detect_neighbor(position, item, data, graph):
    for index, candidate in data.items():
        distance = calc_distance(item, candidate)
        if (distance <= 250) and ((candidate.data[2] >= item.data[2] + 1 and candidate.data[2] <= item.data[2] + 3)):
            graph.add_edge(item, candidate)


def calc_distance(itemA, itemB):
    return math.sqrt((itemB.data[0] - itemA.data[0])**2 + (itemB.data[1] - itemB.data[1])**2)


def detect_noise(graph, dict_frames):
    nodes = np.array(graph.nodes)
    for actual in nodes:
        for neighbor, weight in graph[actual].items():
            for neighbor_n, weight_n in graph[neighbor].items():
                (a, b, c) = calc_parabola_vertex(
                    actual.data, neighbor.data, neighbor_n.data)
                if a is not None and not np.isnan(a) and not np.isinf(a) and abs(a) != 0.0:
                    next_neighbors = dict((key, value) for key, value in dict_frames.items(
                    ) if key > neighbor_n.data[2] and key < neighbor_n.data[2] + 10)
                    if (check_radius(a, b, c, next_neighbors, neighbor_n, neighbor, actual)):
                        actual.noise = False
                        neighbor.noise = False
                        neighbor_n.noise = False
    return nodes


def check_parabola(a, b, c, node):
    y = a*node.data[0]**2 + b*node.data[0] + c
    delta = 5

    if(node.data[1] >= y - delta and node.data[1] <= y + delta):
        return True
    else:
        return False


def check_radius(a, b, c, next_neighbors, actual_node, before_node, b_before_node):
    is_parabola = {}
    for key, neighbors in next_neighbors.items():
        for neighbor in neighbors:
            if (check_parabola(a, b, c, neighbor)):
                if neighbor.data[2] in is_parabola:
                    predict = calc_predict_point(
                        actual_node, before_node, b_before_node)
                    dist_r = calc_distance(
                        predict,  is_parabola[neighbor.data[2]])
                    dist_n = calc_distance(predict, neighbor)
                    print(dist_r)
                    if dist_r > dist_n:
                        is_parabola[neighbor.data[2]] = neighbor
                else:
                    is_parabola[neighbor.data[2]] = neighbor

    if len(is_parabola.keys()) >= 1:
        for key, neighbor in is_parabola.items():
            neighbor.noise = False
        return True
    else:
        return False


def calc_parabola_vertex(first_point, second_point, third_point):
    denom = (first_point[0]-second_point[0]) * (first_point[0] -
                                                third_point[0]) * (second_point[0]-third_point[0])
    if denom == 0.0:
        return None, None, None
    a = (third_point[0] * (second_point[1]-first_point[1]) + second_point[0] *
         (first_point[1]-third_point[1]) + first_point[0] * (third_point[1]-second_point[1])) / denom
    b = (third_point[0]*third_point[0] * (first_point[1]-second_point[1]) + second_point[0]*second_point[0] *
         (third_point[1]-first_point[1]) + first_point[0]*first_point[0] * (second_point[1]-third_point[1])) / denom
    c = (second_point[0] * third_point[0] * (second_point[0]-third_point[0]) * first_point[1]+third_point[0] * first_point[0] *
         (third_point[0]-first_point[0]) * second_point[1]+first_point[0] * second_point[0] * (first_point[0]-second_point[0]) * third_point[1]) / denom

    return a, b, c


def calc_accelerate(actual_point, before_point, b_before_point):
    x_accelerate = ((actual_point.data[0] - before_point.data[0]) - (
        before_point.data[0] - b_before_point.data[0]))/(2.0**2)
    y_accelerate = ((actual_point.data[1] - before_point.data[1]) - (
        before_point.data[1] - b_before_point.data[1]))/(2.0**2)
    return (x_accelerate, y_accelerate)


def calc_velocity(actual_point, before_point, b_before_point, accelerate):
    x_velocity = (actual_point.data[0] -
                  before_point.data[0])/2 + accelerate[0]*2.0
    y_velocity = (actual_point.data[1] -
                  before_point.data[1])/2 + accelerate[1]*2.0
    return (x_velocity, y_velocity)


def calc_predict_point(actual_point, before_point, b_before_point):
    accelerate = calc_accelerate(actual_point, before_point, b_before_point)
    velocity = calc_velocity(actual_point, before_point,
                             b_before_point, accelerate)

    x_point = actual_point.data[0] + velocity[0]*2 + (accelerate[0]*(2.0**2))/2
    y_point = actual_point.data[1] + velocity[1]*2 + (accelerate[1]*(2.0**2))/2
    return Candidate([x_point, y_point])


def calc_angle(point_A, point_B_candidate, point_B_predict):
    m_first = (point_B_predict.data[1] - point_A.data[1]) / \
        (point_B_predict.data[0] - point_A.data[0])
    m_second = (point_B_candidate.data[1] - point_A.data[1]) / \
        (point_B_candidate.data[0] - point_A.data[0])
    angle = math.degrees(
        math.atan(abs((m_second - m_first)/(1 + m_first * m_second))))
    return angle


def calc_s(point_A, point_B_candidate, point_B_predict):
    d = abs(calc_distance(point_B_predict, point_B_candidate))
    dm = 0
    dM = 50
    angle = calc_angle(point_A, point_B_candidate, point_B_predict)

    s1 = np.log2((d-dm)/(dM-dm))
    s2 = np.log2(angle/180.0)
    return(s1, s2)


def create_dicts(array_candidate):
    dict_candidates = {}
    dict_frames = {}
    for index, data in enumerate(array_candidate):
        dict_candidates[index] = Candidate(data)
        if data[2] in dict_frames:
            dict_frames[data[2]].append(dict_candidates[index])
        else:
            dict_frames[data[2]] = [dict_candidates[index]]

    return (dict_candidates, dict_frames)


def create_final_nodes(graph, dict_frames):
    nodes = detect_noise(graph, dict_frames)

    filter_nodes = np.empty((0, 7))
    for node in nodes:
        if not node.noise:
            data = np.append(node.data, np.array(
                [node.noise, node, None, None]))
            filter_nodes = np.append(filter_nodes, np.array([data]), axis=0)

    return filter_nodes


def separate_curves(nodes):
    curves = {}
    code = 0
    nodes_sort = nodes[nodes[:, 2].argsort()]

    for index, node in enumerate(nodes_sort):
        if node[2] > nodes_sort[index - 1][2] + 5 or index == 0:
            code += 1
            curves[code] = {}
            curves[code][node[2]] = [node]
        else:
            if node[2] in curves[code]:
                curves[code][node[2]].append(node)
            else:
                curves[code][node[2]] = [node]

    return curves


def define_direction(curves):
    anterior = (None, None)

    for index, dict_frames in curves.items():
        anterior = [None, None]
        for index_frame, list_frame in dict_frames.items():
            if len(list_frame) > 1:
                distance_min = None
                candidate = None
                for item in list_frame:
                    if (index_frame - 3 in dict_frames and index_frame - 2 in dict_frames and index_frame - 1 in dict_frames):
                        predict_left = calc_predict_point(
                            dict_frames[index_frame - 3][0][4], dict_frames[index_frame - 2][0][4], dict_frames[index_frame - 1][0][4])
                        distance_left = calc_distance(predict_left, item[4])
                    else:
                        distance_left = None

                    if (index_frame + 3 in dict_frames and index_frame + 2 in dict_frames and index_frame + 1 in dict_frames):
                        predict_right = calc_predict_point(
                            dict_frames[index_frame + 1][0][4], dict_frames[index_frame + 2][0][4], dict_frames[index_frame + 3][0][4])
                        distance_right = calc_distance(predict_right, item[4])
                    else:
                        distance_right = None

                    if distance_left is None and distance_right is None:
                        distance = None
                    elif distance_left is not None and distance_right is None:
                        distance = distance_left
                    elif distance_right is not None and distance_left is None:
                        distance = distance_right
                    else:
                        distance = (distance_left + distance_right)/2

                    if distance_min is None:
                        distance_min = distance
                        candidate = item
                    elif distance < distance_min:
                        distance_min = distance
                        candidate = item
                curves[index][index_frame] = [candidate]
            else:
                curves[index][index_frame] = list_frame

            if index_frame - 1 in curves[index] and curves[index][index_frame][0] is not None and curves[index][index_frame - 1][0] is not None:
                if curves[index][index_frame - 1][0][0] < curves[index][index_frame][0][0]:
                    x = DIREITA
                elif curves[index][index_frame - 1][0][0] > curves[index][index_frame][0][0]:
                    x = ESQUERDA
                else:
                    x = anterior[0]

                if curves[index][index_frame - 1][0][1] < curves[index][index_frame][0][1]:
                    y = BAIXO
                elif curves[index][index_frame - 1][0][1] > curves[index][index_frame][0][1]:
                    y = CIMA
                else:
                    y = anterior[1]

                curves[index][index_frame][0][5] = x
                curves[index][index_frame][0][6] = y

    return curves


def check_bounces(curves):
    bounces = []
    for index, candidates in curves.items():
        candidates = list(candidates.items())
        for index_candidate, candidate in enumerate(candidates):
            if index_candidate - 1 >= 0 and index_candidate + 1 < len(candidates) - 1:
                if candidate[1][0][6] == BAIXO and candidate[1][0][5] == ESQUERDA:
                    if candidates[index_candidate - 1][1][0][6] == BAIXO and candidates[index_candidate - 1][1][0][5] == ESQUERDA:
                        if candidates[index_candidate + 1][1][0][6] == CIMA and candidates[index_candidate + 1][1][0][5] == ESQUERDA:
                            bounces.append(candidate)

    return bounces


def start_verification(candidates):
    dict_candidates, dict_frames = create_dicts(candidates)
    graph = create_graph(dict_candidates)
    filter_nodes = create_final_nodes(graph, dict_frames)
    curves = separate_curves(filter_nodes)
    curves = define_direction(curves)
    bounces = check_bounces(curves)

    if (bounces is not None and bounces):
        return bounces
    else:
        return None
