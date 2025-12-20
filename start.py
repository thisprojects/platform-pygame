import pygame
from game import Game

# Initialize Pygame
pygame.init()


def main():
    print("=== Tower Climber Game ===")
    print("Select number of players:")
    print("1. Single Player")
    print("2. Two Players")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "2":
        num_players = 2
        print("\nPlayer 1 Controls: W=Jump, A=Left, D=Right, SPACE=Shoot")
        print("Player 2 Controls: UP=Jump, LEFT=Left, RIGHT=Right, RSHIFT=Shoot")
    else:
        num_players = 1
        print("\nControls: W=Jump, A=Left, D=Right, SPACE=Shoot")

    print("\nSelect map:")
    print("1. Test Map (Quick)")
    print("2. Level 1 (Medium)")
    print("3. Level 2 (Challenging)")

    map_choice = input("Enter choice (1-3): ").strip()
    map_names = {'1': 'test', '2': 'level_1', '3': 'level_2'}
    map_name = map_names.get(map_choice, 'test')

    print("\nObjective: Climb to the top of the tower and reach the yellow exit!")
    print("Defeat enemies along the way!")
    print("Don't fall off the bottom of the screen!")
    print("Starting game...\n")

    game = Game(num_players, map_name)
    game.run()


if __name__ == "__main__":
    main()
