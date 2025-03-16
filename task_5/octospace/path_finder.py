import numpy as np
from queue import PriorityQueue

def find_next_move(game_map, origin, target, search_size):
    prev, new_origin, new_target = find_shortest_paths(game_map, origin, target, search_size)
    path = []
    while new_target != new_origin:
        path.append(new_target)
        new_target = prev[new_target]
    next_pos = path[-1]
    if next_pos[0] > new_origin[0]:
        return 0
    elif next_pos[0] < new_origin[0]:
        return 2
    if next_pos[1] > new_origin[1]:
        return 3
    else:
        return 1

# origin is a tuple (x, y)
# game_map is in the original format received from the game engine
def find_shortest_paths(game_map, origin, target, search_size):
    cut_game_map, origin, target, rect = cut_search_area(game_map, origin, search_size, target)
    nodes = PriorityQueue()
    prev = np.empty(np.shape(cut_game_map), dtype=tuple)
    dist = np.zeros(np.shape(cut_game_map))
    removed = []
    for i in range(len(cut_game_map)):
        for j in range(len(cut_game_map[i])):
            nodes.put((float('inf'), (i, j)))
            dist[i, j] = float('inf')
    nodes.put((0, origin))
    dist[origin] = 0
    while not len(removed) == len(cut_game_map) * len(cut_game_map[0]):
        weight, node = nodes.get()
        if node in removed:
            continue
        removed.append(node)
        x, y = node
        for neigh in get_neighbors(node, cut_game_map):
            if neigh not in removed:
                alt = dist[x, y] + calc_weight(game_map, (x + rect[0][0], y + rect[0][1]), 3)
                if alt < dist[neigh]:
                    dist[neigh] = alt
                    prev[neigh] = node
                    nodes.put((alt, neigh))
        # if node == target:
        #     break

    return prev, origin, target


def cut_search_area(game_map, origin, search_size, target):
    coords = [[origin[0], origin[1]], [target[0], target[1]]] # left top corner, right bottom corner
    coords[0][0] = min(origin[0], target[0])
    coords[0][1] = min(origin[1], target[1])
    coords[1][0] = max(origin[0], target[0])
    coords[1][1] = max(origin[1], target[1])
    if coords[1][0] - coords[0][0] > search_size:
        if origin[0] < target[0]:
            coords[1][0] = origin[0] + search_size
        else:
            coords[0][0] = origin[0] - search_size
    if coords[1][1] - coords[0][1] > search_size:
        if origin[1] < target[1]:
            coords[1][1] = origin[1] + search_size
        else:
            coords[0][1] = origin[1] - search_size
    game_map = game_map[coords[0][0]:coords[1][0]+1, coords[0][1]:coords[1][1]+1]
    new_origin = (origin[0] - coords[0][0], origin[1] - coords[0][1])
    new_target = (target[0] - coords[0][0], target[1] - coords[0][1])
    if origin[0] <= target[0] and origin[1] <= target[1]:
        new_target = (coords[1][0] - coords[0][0], coords[1][1] - coords[0][1])
    elif origin[0] <= target[0] and origin[1] >= target[1]:
        new_target = (coords[1][0] - coords[0][0], 0)
    elif origin[0] >= target[0] and origin[1] <= target[1]:
        new_target = (0, coords[1][1] - coords[0][1])
    elif origin[0] >= target[0] and origin[1] >= target[1]:
        new_target = (0, 0)
    print(coords)
    print(new_origin)
    print(new_target)
    return game_map, new_origin, new_target, coords


def get_neighbors(point, game_map):
    x, y = point
    neighbors = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if x + i < 0 or x + i >= len(game_map) or y + j < 0 or y + j >= len(game_map[0]):
                continue
            neighbors.append((x + i, y + j))
    return neighbors

def calc_weight(game_map, node, def_weight):
    x, y = node
    if game_map[y, x] & int('00000010', 2): # asteroids
        return def_weight + 5
    elif game_map[y, x] & int('00000100', 2): # boost field
        return 0
    return def_weight