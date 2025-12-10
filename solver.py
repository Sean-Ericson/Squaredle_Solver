import numpy as np
import networkx as nx
import pyautogui as pag
import pickle
import time

MIN_WORD_LENGTH = 4

def get_words_by_length():
    with open("words_by_length.pkl", "rb") as f:
        return pickle.load(f)
    with open("words.txt") as f:
        words = [line.strip() for line in f.readlines() if len(line.strip()) >= MIN_WORD_LENGTH]
    max_word_length = max(len(word) for word in words)
    return {i: [w for w in words if len(w) == i] for i in range(MIN_WORD_LENGTH, max_word_length + 1)}

def string_to_grid(grid_str):
    grid_list = [c if c != ' ' else '' for c in grid_str]
    l = int(np.sqrt(len(grid_list)))
    return np.array(grid_list).reshape(l,l)

def create_grid_with_diagonals(rows, cols):
    G = nx.grid_2d_graph(rows, cols)
    for r in range(rows):
        for c in range(cols):
            if r > 0 and c > 0:
                G.add_edge((r, c), (r - 1, c - 1))
            # Top-right diagonal
            if r > 0 and c < cols - 1:
                G.add_edge((r, c), (r - 1, c + 1))
            # Bottom-left diagonal
            if r < rows - 1 and c > 0:
                G.add_edge((r, c), (r + 1, c - 1))
            # Bottom-right diagonal
            if r < rows - 1 and c < cols - 1:
                G.add_edge((r, c), (r + 1, c + 1))
    return G

def create_graph(grid):
    graph = create_grid_with_diagonals(*grid.shape)
    for node in list(graph.nodes):
        x,y = node
        graph.nodes[node]['letter'] = grid[x,y]
        if grid[x,y] == '': 
            graph.remove_node(node)
    return graph

def find_word_paths(graph, words_by_length):
    word_paths = {}

    def determine_consistent_words(current_words_by_len, current_string):
        return {i: [w for w in current_words_by_len[i] if w.startswith(current_string)] for i in range(max(len(current_string), 4), max(words_by_length.keys()) + 1)}

    def recursive_search(current_path, current_graph, consistent_words):
        #print(current_string, current_node, consistent_words.keys())
        if all(len(consistent_words[i]) == 0 for i in consistent_words.keys()):
            return
        current_node = current_path[-1]
        current_string = "".join(graph.nodes[n]['letter'] for n in current_path)
        for neighbor in current_graph.neighbors(current_node):
            next_string = current_string + graph.nodes[neighbor]['letter']
            next_path = current_path + [neighbor]
            if next_string == '':
                print(current_path, next_path)
                raise ValueError("ahh")
            if len(next_string) >= MIN_WORD_LENGTH and next_string in consistent_words[len(next_string)]:
                if next_string not in word_paths:
                    word_paths[next_string] = [next_path]
                else:
                    word_paths[next_string].append(next_path)
            next_consistent_words = determine_consistent_words(consistent_words, next_string)
            new_graph = current_graph.copy()
            new_graph.remove_node(current_node)
            recursive_search(next_path, new_graph, next_consistent_words)

    for node in graph.nodes:
        new_graph = graph.copy()
        new_graph.remove_node(node)
        recursive_search([node], graph, words_by_length)

    return word_paths

def solve(grid_str, return_paths=False) -> dict[str, list[list[tuple[int, int]]]] | list[str]:
    words_by_length = get_words_by_length()
    grid = string_to_grid(grid_str)
    graph = create_graph(grid)
    word_paths = find_word_paths(graph, words_by_length)
    if return_paths:
        return word_paths
    return list(word_paths.keys())

def solve_and_autoclick(grid_str, delay=2):
    found_words = solve(grid_str)
    time.sleep(delay)
    for word in found_words:
        pag.press('esc')
        pag.write(word)
        pag.press('enter')
