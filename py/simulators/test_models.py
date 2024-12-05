import numpy as np

class Player:
    """
    Represents a tennis player with relevant serving and returning statistics.
    """
    def __init__(self, name, first_serve_percentage, ace_percentage,
                 first_serve_win_percentage, second_serve_win_percentage,
                 double_fault_percentage, return_points_won_percentage):
        self.name = name
        self.first_serve_percentage = first_serve_percentage  # Probability of using first serve
        self.ace_percentage = ace_percentage  # Probability of serving an ace on first serve
        self.first_serve_win_percentage = first_serve_win_percentage  # Probability of winning a point on first serve
        self.second_serve_win_percentage = second_serve_win_percentage  # Probability of winning a point on second serve
        self.double_fault_percentage = double_fault_percentage  # Probability of double faulting
        self.return_points_won_percentage = return_points_won_percentage  # Probability of winning a point on return

def simulate_game(server: Player, returner: Player):
    """
    Simulates a single tennis game between server and returner with detailed logs.

    Args:
        server (Player): The player serving the game.
        returner (Player): The player receiving the serve.

    Returns:
        str: Name of the player who won the game.
    """
    # Initialize scores
    score_map = {0: '0', 1: '15', 2: '30', 3: '40'}
    server_points = 0
    returner_points = 0
    point_number = 1  # To track point sequence
    advantage = None  # None, 'server', or 'returner'

    print(f"Starting game: {server.name} (Server) vs {returner.name} (Returner)\n")

    while True:
        print(f"--- Point {point_number} ---")
        point_number += 1

        # Debug: Current points before the point
        print(f"Current Points -> {server.name}: {score_map.get(server_points, '40+')} , {returner.name}: {score_map.get(returner_points, '40+')}")
        
        # Check for Deuce or Advantage before serving
        if server_points >=3 and returner_points >=3:
            if advantage is None:
                print("DEUCE!")
            elif advantage == 'server':
                print(f"{server.name} has ADVANTAGE.")
            elif advantage == 'returner':
                print(f"{returner.name} has ADVANTAGE.")
        
        # Determine if it's a first serve or second serve
        if np.random.rand() < server.first_serve_percentage:
            # First serve
            serve_type = "First Serve"
            print(f"{server.name} is attempting a first serve.")
            if np.random.rand() < server.ace_percentage:
                # Ace
                print(f"{server.name} serves an ACE!")
                point_winner = server
            else:
                # Not an ace, determine if the serve is in or a fault
                if np.random.rand() > server.first_serve_win_percentage:
                    # Fault
                    print(f"{server.name} faults the first serve.")
                    # Second serve attempt
                    if np.random.rand() < server.double_fault_percentage:
                        # Double Fault
                        print(f"{server.name} commits a DOUBLE FAULT!")
                        point_winner = returner
                    else:
                        # Second serve in
                        print(f"{server.name} is attempting a second serve.")
                        if np.random.rand() < server.second_serve_win_percentage:
                            # Win the point on second serve
                            print(f"{server.name} wins the point on second serve.")
                            point_winner = server
                        else:
                            # Second serve failed (Double Fault)
                            print(f"{server.name} fails the second serve.")
                            point_winner = returner
                else:
                    # Serve is in, determine if point is won
                    if np.random.rand() < server.first_serve_win_percentage:
                        # Server wins the point
                        print(f"{server.name} wins the point on first serve.")
                        point_winner = server
                    else:
                        # Returner wins the point
                        print(f"{returner.name} wins the point on {server.name}'s first serve.")
                        point_winner = returner
        else:
            # Second serve
            serve_type = "Second Serve"
            print(f"{server.name} is attempting a second serve.")
            if np.random.rand() < server.second_serve_win_percentage:
                # Win the point on second serve
                print(f"{server.name} wins the point on second serve.")
                point_winner = server
            else:
                # Double fault
                print(f"{server.name} commits a DOUBLE FAULT on second serve!")
                point_winner = returner

        # Update points based on who won the point
        if point_winner == server:
            if server_points < 3 or returner_points < 3:
                server_points += 1
                print(f"{server.name} wins the point. Score: {server.name} {score_map.get(server_points, '40')}, {returner.name} {score_map.get(returner_points, '0')}\n")
            else:
                if advantage == 'server':
                    print(f"{server.name} wins the game!\n")
                    return server.name
                elif advantage == 'returner':
                    advantage = None
                    print("DEUCE!\n")
                else:
                    advantage = 'server'
                    print(f"{server.name} gains ADVANTAGE.\n")
        else:
            if returner_points < 3 or server_points < 3:
                returner_points += 1
                print(f"{returner.name} wins the point. Score: {server.name} {score_map.get(server_points, '0')}, {returner.name} {score_map.get(returner_points, '40')}\n")
            else:
                if advantage == 'returner':
                    print(f"{returner.name} wins the game!\n")
                    return returner.name
                elif advantage == 'server':
                    advantage = None
                    print("DEUCE!\n")
                else:
                    advantage = 'returner'
                    print(f"{returner.name} gains ADVANTAGE.\n")

        # Check for game win conditions outside Deuce
        if server_points >= 4 and server_points - returner_points >= 2:
            print(f"Game won by {server.name}!\n")
            return server.name
        elif returner_points >= 4 and returner_points - server_points >= 2:
            print(f"Game won by {returner.name}!\n")
            return returner.name

def main():
    # Define dummy statistics for two players
    # Player 1: Aggressive Player
    player1 = Player(
        name="Player 1",
        first_serve_percentage=0.7,  # 70% chance to use first serve
        ace_percentage=0.1,  # 10% chance to ace the serve
        first_serve_win_percentage=0.75,  # 75% chance to win the point on first serve
        second_serve_win_percentage=0.55,  # 55% chance to win the point on second serve
        double_fault_percentage=0.03,  # 3% chance to double fault
        return_points_won_percentage=0.25  # 25% chance to win the point on return
    )
    
    # Player 2: Defensive Player
    player2 = Player(
        name="Player 2",
        first_serve_percentage=0.6,  # 60% chance to use first serve
        ace_percentage=0.05,  # 5% chance to ace the serve
        first_serve_win_percentage=0.65,  # 65% chance to win the point on first serve
        second_serve_win_percentage=0.6,  # 60% chance to win the point on second serve
        double_fault_percentage=0.025,  # 2.5% chance to double fault
        return_points_won_percentage=0.4  # 40% chance to win the point on return
    )
    
    # Simulate a game where Player 1 is serving
    print("Simulating game: Player 1 (Server) vs Player 2 (Returner)\n")
    game_winner = simulate_game(server=player1, returner=player2)
    print(f"Game Winner: {game_winner}\n")
    
    # Simulate a game where Player 2 is serving
    print("Simulating game: Player 2 (Server) vs Player 1 (Returner)\n")
    game_winner = simulate_game(server=player2, returner=player1)
    print(f"Game Winner: {game_winner}\n")

if __name__ == "__main__":
    main()

