import arcade
from src import GamePanel


def main():

    game = GamePanel()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()