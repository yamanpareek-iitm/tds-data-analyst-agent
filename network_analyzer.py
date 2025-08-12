import pandas as pd
import networkx as nx
import numpy as np
import io, base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from plot_utils import png_base64_under_limit

def handle_network_task(qtext: str, csv_path: str) -> dict:
    # Load edge list
    df = pd.read_csv(csv_path)
    # Build undirected graph
    G = nx.Graph()
    G.add_edges_from(df.values.tolist())
    
    nodes = list(G.nodes())
    degrees = dict(G.degree())
    
    # 1. Edge count
    edge_count = G.number_of_edges()
    
    # 2. Highest degree node
    highest_degree_node = max(degrees.items(), key=lambda kv: kv[1])[0] if degrees else ""
    
    # 3. Average degree
    average_degree = float(np.mean(list(degrees.values()))) if degrees else 0.0
    
    # 4. Density
    density = float(nx.density(G))
    
    # 5. Shortest path Alice-Eve (case-insensitive match)
    nodelc = {name.lower(): name for name in nodes}
    src = nodelc.get("alice")
    tgt = nodelc.get("eve")
    try:
        shortest = nx.shortest_path_length(G, src, tgt)
    except Exception:
        shortest = -1

    # 6. Network graph (nodes labelled, edges as in CSV)
    fig1, ax1 = plt.subplots(figsize=(5,4))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, ax=ax1, with_labels=True, node_size=800, node_color="skyblue",
            font_size=10, font_color="black", edge_color="gray", width=2)
    ax1.set_title("Network Graph")
    ax1.axis('off')
    net_b64 = png_base64_under_limit(fig1)
    
    # 7. Degree histogram (green bars)
    deg_counts = pd.Series(list(degrees.values())).value_counts().sort_index()
    fig2, ax2 = plt.subplots(figsize=(4,3))
    deg_counts.plot(kind="bar", color="green", ax=ax2)
    ax2.set_xlabel("Degree")
    ax2.set_ylabel("Node Count")
    ax2.set_title("Degree Distribution")
    plt.tight_layout()
    hist_b64 = png_base64_under_limit(fig2)

    return {
        "edge_count": edge_count,
        "highest_degree_node": str(highest_degree_node),
        "average_degree": average_degree,
        "density": density,
        "shortest_path_alice_eve": shortest,
        "network_graph": net_b64,
        "degree_histogram": hist_b64,
    }
