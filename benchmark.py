import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import io
import pygame

from environment import GraphEnvironment, GraphTopology
from bfs_agent import BFS_SearchAgent
from dfs_agent import DFS_SearchAgent
from iddfs_agent import IDDFS_SearchAgent
from greedy_agent import Greedy_SearchAgent
from astar_agent import AStar_SearchAgent

matplotlib.use("Agg") # Headless render backend

def run_headless_batch(algorithms, complexity, runs, callback=None):
    results = {}
    
    if complexity == "Easy":
        size = 20
        branching = 2
    elif complexity == "Medium":
        size = 100
        branching = 3
    else: # Hard
        size = 500
        branching = 5
        
    for alg in algorithms:
        results[alg] = {
            'times': [],
            'expanded': [],
            'path_length': []
        }
        
    for run in range(runs):
        seed = 10000 + run
        
        env = GraphEnvironment(size=size, seed=seed, topology=GraphTopology.TREE, branching_factor=branching)
        
        for alg in algorithms:
            if alg == "BFS":
                agent = BFS_SearchAgent(env, env.start_node)
            elif alg == "DFS":
                agent = DFS_SearchAgent(env, env.start_node)
            elif alg == "ID-DFS":
                agent = IDDFS_SearchAgent(env, env.start_node)
            elif alg == "Greedy":
                agent = Greedy_SearchAgent(env, env.start_node, use_euclidean=False)
            elif alg == "A*":
                agent = AStar_SearchAgent(env, env.start_node, use_euclidean=False)
            else:
                continue

            start_t = time.perf_counter()
            while not agent.is_finished:
                pygame.event.pump()
                agent.step()
                if callback:
                    callback()
            end_t = time.perf_counter()
            
            results[alg]['times'].append(end_t - start_t)
            visited_len = len(getattr(agent, 'visited', []))
            results[alg]['expanded'].append(visited_len)
            path_len = len(getattr(agent, 'path', [])) if getattr(agent, 'path', []) else 0
            results[alg]['path_length'].append(path_len)
            
    aggregated = {}
    for alg, data in results.items():
        if not data['times']: continue
        aggregated[alg] = {
            'mean_time': np.mean(data['times']),
            'std_time': np.std(data['times']),
            'mean_expanded': np.mean(data['expanded']),
            'std_expanded': np.std(data['expanded'])
        }
        
    return aggregated

def generate_chart_surface(aggregated_data):
    if not aggregated_data:
        return None
        
    labels = list(aggregated_data.keys())
    means = [aggregated_data[alg]['mean_time'] for alg in labels]
    stds = [aggregated_data[alg]['std_time'] for alg in labels]
    
    fig, ax = plt.subplots(figsize=(4.5, 3.5), dpi=100)
    fig.patch.set_facecolor('#2563eb') 
    ax.set_facecolor('#2563eb')
    
    bars = ax.bar(labels, means, yerr=stds, capsize=5, color='white', alpha=0.9, ecolor='white')
    
    ax.set_ylabel('Mean execution time (s)', color='white')
    ax.set_title('Algorithm Performance Comparison', color='white')
    ax.tick_params(colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    
    try:
        surf = pygame.image.load(buf, 'png').convert_alpha()
        return surf
    except Exception:
        return None
