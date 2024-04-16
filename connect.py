import tkinter as tk
from tkinter import Entry, Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import random

def create_mlp_graph(num_input_layers, num_hidden_layers, num_neurons_per_layer):
    G = nx.DiGraph()

    # Add input layer nodes
    input_nodes = [f'Input{i}' for i in range(1, num_input_layers + 1)]
    G.add_nodes_from(input_nodes, subset='input')

    # Add hidden layers and connect them
    for layer in range(1, num_hidden_layers + 1):
        layer_nodes = [f'Hidden{layer}_{i}' for i in range(1, num_neurons_per_layer + 1)]
        G.add_nodes_from(layer_nodes, subset='hidden')

        if layer == 1:
            # Connect input layer to the first hidden layer
            for input_node in input_nodes:
                for layer_node in layer_nodes:
                    G.add_edge(input_node, layer_node, weight=0.5)
        else:
            # Connect previous hidden layer to the current hidden layer
            prev_layer_nodes = [f'Hidden{layer - 1}_{i}' for i in range(1, num_neurons_per_layer + 1)]
            for prev_node in prev_layer_nodes:
                for current_node in layer_nodes:
                    G.add_edge(prev_node, current_node, weight=0.5)

    return G

def get_random_path(graph, start_node):
    path = [start_node]
    current_node = start_node

    while True:
        neighbors = list(graph.neighbors(current_node))
        if not neighbors:
            break
        next_node = random.choice(neighbors)
        path.append(next_node)
        current_node = next_node

    return path

# Create an MLP-like graph with 5 input nodes, 5 hidden layers (each with 5 neurons), and 1 output node
mlp_graph = create_mlp_graph(num_input_layers=5, num_hidden_layers=5, num_neurons_per_layer=5)

# Set color and border attributes for all nodes
for node, data in mlp_graph.nodes(data=True):
    mlp_graph.nodes[node]['color'] = 'white'
    mlp_graph.nodes[node]['border_color'] = 'black'

# Create a custom grid layout
pos = {}
for i, node in enumerate(mlp_graph.nodes()):
    row = i // 5  # Adjust the number of nodes per row as needed
    col = i % 5
    pos[node] = (col, -row)

# Create a Tkinter window
root = tk.Tk()
root.title("Connect Four - MLP Graph")

# Create a Matplotlib figure with larger size
fig, ax = plt.subplots(figsize=(6, 5))
ax.set_title("Connect Four - MLP Graph")

# Draw the graph on the Matplotlib figure with custom grid layout
nx.draw_networkx_nodes(mlp_graph, pos, node_color=[mlp_graph.nodes[n]['color'] for n in mlp_graph.nodes], node_size=800, ax=ax, edgecolors=[mlp_graph.nodes[n]['border_color'] for n in mlp_graph.nodes], linewidths=2)
nx.draw_networkx_edges(mlp_graph, pos, edge_color='gray', ax=ax, arrowsize=20)

# Create a Tkinter canvas for the Matplotlib figure
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Add a toolbar (optional)
toolbar = tk.Frame(root)
toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=0)
toolbar.update()

# Entry and Button for user input
label1 = tk.Label(root, text="Player 1: Enter Node Number (1-5):")
label1.pack(side=tk.LEFT, padx=10)
entry1 = Entry(root)
entry1.pack(side=tk.LEFT, padx=10)
button1 = Button(root, text="Drop Piece", command=lambda: drop_piece(1))
button1.pack(side=tk.LEFT, padx=10)

label2 = tk.Label(root, text="Player 2: Enter Node Number (1-5):")
label2.pack(side=tk.LEFT, padx=10)
entry2 = Entry(root)
entry2.pack(side=tk.LEFT, padx=10)
button2 = Button(root, text="Drop Piece", command=lambda: drop_piece(2))
button2.pack(side=tk.LEFT, padx=10)

def drop_piece(player):
    try:
        entry = entry1 if player == 1 else entry2
        player_node = f'Input{int(entry.get())}'

        # Get random path for the player
        path = get_random_path(mlp_graph, player_node)

        # Update colors for the player nodes
        color = 'red' if player == 1 else 'blue'
        for i, node in enumerate(path):
            if mlp_graph.nodes[node]['color'] == 'white':
                # If it's the last node in the last layer, color it explicitly
                if i == len(path) - 1 and 'Hidden' in node:
                    mlp_graph.nodes[node]['color'] = color
                    nx.draw_networkx_nodes(mlp_graph, pos, nodelist=[node], node_color=color, node_size=800, ax=ax, edgecolors='black', linewidths=2)
                    canvas.draw()
                    root.update()
                    plt.pause(0.5)
                    print(f"Player {player}: Node {node} colored in the last layer.")
                    break  # Break the loop after coloring the final node

                # Track the final position of the node and piece color
                if 'Hidden' in node and i == len(path) - 1:
                    mlp_graph.nodes[node]['final_position'] = color
                    print(f"Player {player}: Node {node} is the final position.")

            elif 'Hidden' in node:  # If the next node is already colored
                # Choose some other node in the same layer
                layer_nodes = [n for n in mlp_graph.nodes if f'Hidden{player}' in n]
                available_nodes = [n for n in layer_nodes if mlp_graph.nodes[n]['color'] == 'white']
                
                if available_nodes:
                    next_node = random.choice(available_nodes)
                    path[i] = next_node
                else:
                    break  # If all nodes in the layer are colored, break the loop

        root.update()
        plt.pause(0.5)  # Pause for a short duration to visualize one step at a time

    except ValueError:
        print("Please enter a valid node number.")


# Display the window
root.mainloop()
