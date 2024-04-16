import networkx as nx
import matplotlib.pyplot as plt
import random

def initialize_board():
    G = nx.DiGraph()
    for i in range(6):
        for j in range(6):
            G.add_node((i, j), piece=None)
            if i < 5:
                for k in range(6):
                    # cerate a random number for the edge
                    # if random value < p value : then write the edge 
                    a = random.uniform(0.1, 0.9)
                    if a < 0.4:
                        G.add_edge((i, j), (i + 1, k))
    return G

def print_board(G):
    for i in range(6):
        for j in range(6):
            piece = G.nodes[(i, j)]['piece']
            print(f"{piece if piece else '-'}", end=" ")
        print()

def visualize_board(G):
    node_colors = []
    for node in G.nodes:
        piece = G.nodes[node]['piece']
        if piece == 'R':
            node_colors.append('red')
        elif piece == 'B':
            node_colors.append('blue')
        else:
            node_colors.append('white')

    pos = {node: (node[1], -node[0]) for node in G.nodes}
    nx.draw(G, pos, with_labels=False, node_size=700, node_color=node_colors, edgecolors='black')
    plt.show()
    plt.close(2)



def drop_piece(G, column, player):
    path_taken = []
    
    # First, occupy the specified node
    node = (0, column)
    path_taken.append(node)

    # Travel down the graph randomly among unoccupied neighbors
    while True:
        neighbors = list(G.neighbors(node))
        unoccupied_neighbors = [neighbor for neighbor in neighbors if G.nodes[neighbor]['piece'] is None]

        if not unoccupied_neighbors:
            break  # No unoccupied neighbors, reached the last unoccupied node

        chosen_neighbor = random.choice(unoccupied_neighbors)
        path = nx.shortest_path(G, source=node, target=chosen_neighbor)
        path_taken.extend(path[1:])
        node = chosen_neighbor

    # Mark only the final node as occupied
    G.nodes[path_taken[-1]]['piece'] = player

    return path_taken

def is_winner(G, player):
    for node in G.nodes:
        if G.nodes[node]['piece'] == player:
            if check_winning_sequence(G, node, player, set()):
                return True
    return False

def check_winning_sequence(G, start_node, player, visited):
    visited.add(start_node)

    if len(visited) == 4:
        return True

    for neighbor in G.neighbors(start_node):
        if G.nodes[neighbor]['piece'] == player and neighbor not in visited:
            if check_winning_sequence(G, neighbor, player, visited.copy()):
                return True

    return False

def suggest_best_move(G, player):
    best_move = None
    max_score = -1

    for column in range(6):
        for row in range(5, -1, -1):  # Start from the bottom
            if G.nodes[(row, column)]['piece'] is None:
                score = calculate_move_score(G, column, row, player)
                if score > max_score:
                    max_score = score
                    best_move = (column, row)

                break  # Move to the next column after finding an unoccupied row

    return best_move

def calculate_move_score(G, column, row, player):
    # Basic scoring heuristic example: count the number of pieces in potential winning sequences
    score = 0

    for neighbor in G.neighbors((row, column)):
        if G.nodes[neighbor]['piece'] == player:
            score += 1

    return score

def play_connect_four():
    G = initialize_board()
    players = ['R', 'B']
    turn = 0

    while True:
        visualize_board(G)
        print_board(G)
        player = players[turn % 2]

        # Suggest a move based on the search algorithm

        suggested_move = suggest_best_move(G, player)
        print(f"Suggested move for {player}: {suggested_move[0]}")

        win_probabilities_player = calculate_win_probabilities(G, player)
        opponent = "R" if player == "B" else "B"
        win_probabilities_opponent = calculate_win_probabilities(G, opponent)

        print(f"Win Probabilities for {player}: {win_probabilities_player}")
        print(f"Win Probabilities for {opponent}: {win_probabilities_opponent}") 
        # User input
        column = -1
        while column not in range(6):
            try:
                column = int(input(f"{player}'s turn. Enter the column (0-5): "))
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

        row = suggested_move[1]
        if G.nodes[(0, column)]['piece'] is None and row is not None:

            drop_piece(G, column, player)

            if is_winner(G, player):
                visualize_board(G)
                print_board(G)
                print(f"{player} wins!")
                break

            turn += 1
        else:
            print("Invalid move. Please choose another column.")

def calculate_win_probabilities(G, player):
    win_probabilities = {}
    probab = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, }
    n = 50

    for x in range(n):
        for column in range(6):
            if G.nodes[(0, column)]["piece"] is None:
                # Simulate dropping a piece in the current column
                temp_G = G.copy()
                drop_piece(temp_G, column, player)

                # Check if the move results in a win for the player
                if is_winner(temp_G, player):
                    win_probabilities[column] = 1.0
                    probab[column] += 1.0
                else:
                    # Simulate opponent's move and check if it leads to their win
                    opponent = "R" if player == "B" else "B"
                    opponent_wins = any(is_winner(temp_G, opponent) for _ in range(100))

                    # Assign win probability based on the opponent's likelihood of winning
                    if opponent_wins:
                        win_probabilities[column] = 0.0
                        probab[column] += 0.0
                    else:
                        win_probabilities[column] = 0.5  # Assuming a tie
                        probab[column] += 0.5

    for column in range(6):
        probab[column] = probab[column] / n

    return probab


    
if __name__ == "__main__":
    play_connect_four()
