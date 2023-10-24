"""
Overall control for 2048 clone 512.  Coordinates
model and view and implements controller
functionality by interpreting keyboard input
"""
import model
import view
import keypress
import sys


def main():
    # Set up model component
    grid = model.Board()
    # Set up view component
    game_view = view.GameView(600, 600)
    grid_view = view.GridView(game_view, len(grid.tiles))
    grid.add_listener(grid_view)
    # Handle control component responsibility here
    commands = keypress.Command(game_view)

    # FIXME: We will change this to 
    #  grid.place_tile(value=2) after
    #  creating the keyword argument in model.py
    grid.place_tile()

    # Game continues until there is no empty
    # space for a tile
    while grid.has_empty():
        grid.place_tile()
        cmd = commands.next()
        if cmd == keypress.LEFT:
            grid.left()
        elif cmd == keypress.RIGHT:
            grid.right()
        elif cmd == keypress.UP:
            grid.up()
        elif cmd == keypress.DOWN:
            grid.down()
        elif cmd == keypress.CLOSE:
            # Ended game by closing window
            print(f"Your score: {grid.score()}")
            sys.exit(0)
        else: 
            assert cmd == keypress.UNMAPPED

    game_view.lose(grid.score())


if __name__ == "__main__":
    main()
