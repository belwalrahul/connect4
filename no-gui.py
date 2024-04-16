import networkx as nx
import matplotlib.pyplot as plt
import os
import random
import csv

def initialize_board(p_value):
    G = nx.DiGraph()
    for i in range(6):
        for j in range(6):
            G.add_node((i, j), piece=None)
            if i < 5:
                for k in range(6):
                    # cerate a random number for the edge
                    # if random value < p value : then write the edge
                    a = random.uniform(0.1, 0.9)
                    if a < p_value:
                        G.add_edge((i, j), (i + 1, k))
    return G


def print_board(G):
    for i in range(6):
        for j in range(6):
            piece = G.nodes[(i, j)]["piece"]
            print(f"{piece if piece else '-'}", end=" ")
        print()


def visualize_board(G):
    node_colors = []
    for node in G.nodes:
        piece = G.nodes[node]["piece"]
        if piece == "R":
            node_colors.append("red")
        elif piece == "B":
            node_colors.append("blue")
        else:
            node_colors.append("white")

    pos = {node: (node[1], -node[0]) for node in G.nodes}
    nx.draw(
        G,
        pos,
        with_labels=False,
        node_size=700,
        node_color=node_colors,
        edgecolors="black",
    )
    plt.show()

def calculate_win_probabilities(G, player):
    win_probabilities = {}

    for column in range(6):
        if G.nodes[(0, column)]["piece"] is None:
            # Simulate dropping a piece in the current column
            temp_G = G.copy()
            drop_piece(temp_G, column, player)

            # Check if the move results in a win for the player
            if is_winner(temp_G, player):
                win_probabilities[column] = 1.0
            else:
                # Simulate opponent's move and check if it leads to their win
                opponent = "R" if player == "B" else "B"
                opponent_wins = any(is_winner(temp_G, opponent) for _ in range(100))

                # Assign win probability based on the opponent's likelihood of winning
                if opponent_wins:
                    win_probabilities[column] = 0.0
                else:
                    win_probabilities[column] = 0.5  # Assuming a tie

    return win_probabilities

def drop_piece(G, column, player):
    path_taken = []

    # First, occupy the specified node
    node = (0, column)
    path_taken.append(node)

    # Travel down the graph randomly among unoccupied neighbors
    while True:
        neighbors = list(G.neighbors(node))
        unoccupied_neighbors = [
            neighbor for neighbor in neighbors if G.nodes[neighbor]["piece"] is None
        ]

        if not unoccupied_neighbors:
            break

        chosen_neighbor = random.choice(unoccupied_neighbors)
        path = nx.shortest_path(G, source=node, target=chosen_neighbor)
        path_taken.extend(path[1:])
        node = chosen_neighbor

    G.nodes[path_taken[-1]]["piece"] = player

    return path_taken


def is_winner(G, player):
    for node in G.nodes:
        if G.nodes[node]["piece"] == player:
            if check_winning_sequence(G, node, player, set()):
                return True
    return False


def check_winning_sequence(G, start_node, player, visited):
    visited.add(start_node)

    if len(visited) == 4:
        return True

    for neighbor in G.neighbors(start_node):
        if G.nodes[neighbor]["piece"] == player and neighbor not in visited:
            if check_winning_sequence(G, neighbor, player, visited.copy()):
                return True

    return False

def get_winning_nodes(G, player):
    winning_nodes = []

    for node in G.nodes:
        if G.nodes[node]["piece"] == player:
            if check_winning_sequence(G, node, player, set()):
                # print(nx.shortest_path(G, source=node, target=None))
                winning_nodes.extend(nx.shortest_path(G, source=node, target=None))
    return winning_nodes

def play_connect_four():
    G = initialize_board()
    players = ["R", "B"]
    turn = 0

    while True:
        # visualize_board(G)
        # print_board(G)
        player = players[turn % 2]
        column = int(input(f"{player}'s turn. Enter the column (0-5): "))

        if 0 <= column <= 5 and drop_piece(G, column, player):
            if is_winner(G, player):
                visualize_board(G)
                print_board(G)
                print(f"{player} wins!")
                break
            turn += 1
        else:
            print("Invalid move. Try again.")

def calculate_clustering_coefficient(G):
    return (nx.average_clustering(G))


def simulate_single_game_with_centrality(p_value):
    G = initialize_board(p_value)
    players = ["R", "B"]
    turn = 0
    total_centrality_values = []
    ev_ret = 0
    # visualize_board(G)
    # print_board(G)

    while True:
        # visualize_board(G)
        # print_board(G)
        player = players[turn % 2]
        column = random.randint(0, 5)
        isolates = nx.number_of_isolates(G)

        if 0 <= column <= 5 and drop_piece(G, column, player):
            win_probabilities_player = calculate_win_probabilities(G, player)
            opponent = "R" if player == "B" else "B"
            win_probabilities_opponent = calculate_win_probabilities(G, opponent)

            print(f"Win Probabilities for {player}: {win_probabilities_player}")
            print(f"Win Probabilities for {opponent}: {win_probabilities_opponent}")

            if is_winner(G, player):
                winning_nodes = get_winning_nodes(G, player)
                centrality_values = calculate_degree_centrality(G, winning_nodes)

                return player, turn, centrality_values, isolates
            turn += 1
            if turn == 36:
                return "Tie", turn, [], isolates
        else:
            pass

def calculate_degree_centrality(G, nodes):
    centrality_values = [nx.degree_centrality(G)[node] for node in nodes]
    return centrality_values

def simulate_connect_four_multiple_times_to_csv():

    # Specify the CSV file path
    csv_file_path = "connect_four_results.csv"

    with open(csv_file_path, mode='w', newline='') as csv_file:
        fieldnames = ["P Value", "Player R Wins", "Player B Wins", "Ties", "Avg No. of Moves", "Avg Degree Centrality", "Avg Isolate count"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        # for i in range(2, 21, 1):
        results = {"R": 0, "B": 0, "Tie": 0}
        num_moves_total = 0
        total_num_moves = 0
        total_centrality_values = []
        total_isolates = []
        p_value = 0.3

        for c in range(10):
            print(c)
            winner, num_moves, centrality_values, isolates = simulate_single_game_with_centrality(p_value)
            num_moves_total += num_moves
            total_num_moves += 1
            results[winner] += 1
            total_isolates.append(isolates)
            total_centrality_values.extend(centrality_values)

        avg_isolates = sum(total_isolates)/len(total_isolates)
        avg_degree_centrality = sum(total_centrality_values) / len(total_centrality_values) if total_centrality_values else 0

        # Write the results to the CSV file
        writer.writerow({
            "P Value": p_value,
            "Player R Wins": results["R"],
            "Player B Wins": results["B"],
            "Ties": results["Tie"],
            "Avg No. of Moves": num_moves_total / total_num_moves,
            "Avg Degree Centrality": avg_degree_centrality,
            "Avg Isolate count":avg_isolates
        })

if __name__ == "__main__":
    simulate_connect_four_multiple_times_to_csv()


#algorithm
'''
call to simulation function
    for p values from 0.1 to 0.9:
        for game from 0 to 1 million
            call to individual game
                initialize the board
                call to drop piece --> returns path taken
                    start at the node user selected and occupy that temporarily
                    choose a random unoccupied neighbour of that node, if no unoccupied neighbours, just occupy current node
                    mark final node as occupied
                check if player is winner:
                    runs dfs starting at each node in graph to find 4 in a sequence

        write game data to csv

'''