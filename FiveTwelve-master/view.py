"""
View component of 512 (2048 clone).  Responsible for
graphical depiction of game state. Some parts of this
could be factored out into a style component if we
wanted to provide more configurability.

"""

import graphics.graphics as graphics
import time
import game_element
import model
from typing import Tuple

##########################
# Configuration constants
#########################

WIN_TITLE = "Five Twelve"
WIN_HEIGHT = 800
WIN_WIDTH = 800
MARGIN = WIN_HEIGHT * 0.04  # around each cell
BACKGROUND_COLOR = "wheat"

# Appearance of tiles. Color ramp is from
# http://colorbrewer2.org/#type=sequential&scheme=Reds&n=9
TILE_OUTLINE_NEW = "#ff0000"
TILE_OUTLINE_OLD = BACKGROUND_COLOR
# Tile color changes as value increases
RAMP = {2: '#fff5f0', 4: '#fff5f0',
        8: '#fee0d2', 16: '#fee0d2',
        32: '#fcbba1',
        64: '#fc9272',
        128: '#fb6a4a',
        256: '#ef3b2c',
        512: '#cb181d',
        1024: '#a50f15',
        2048: '#67000d',
        # If anyone gets farther, we use the same color
        4096: '#67000d',  8192: '#67000d', 16384: '#67000d',
        # I'm prepared to gamble that nobody can reach 2^16
        32768: "#ff0000", 65536: "#ff0000"
        }

# For animating sliding tiles
ANIMATION_STEPS = 3
ANIMATION_TIME = 0.05

#######
# End configuration constants
######

# Events we need to respond to:
#   - A new tile has been created.  Draw it and listen to it.
#   - A tile has been removed (maybe swallowed by another).
#   - A tile has been updated. Update its position and/or value.
#


class GameView(object):
    """The overall view (game window)"""

    def __init__(self, height=WIN_HEIGHT, width=WIN_WIDTH):
        """The GameView is associated with a GraphWin"""
        self.height = height
        self.width = width
        self.win = graphics.GraphWin(WIN_TITLE, width, height)

    def get_key(self) -> str:
        """Acquire a single keystroke as a string,
        e.g., "e" for the "e" key.  Some keys are
        encoded as strings, e.g., "Left" for the left
        arrow key.  Encoding conventions are from TkInter.
        """
        return self.win.getKey()

    def close(self):
        """Do this last; further interaction with the view
        after 'close' is an arrow.
        """
        self.win.close()

    def lose(self, score=0):
        """Display 'Game Over' and close after next keystroke"""
        center = graphics.Point(self.width / 2.0, self.height / 2.0)
        if score:
            goodbye = "Game over. Your score: {}".format(score)
        else:
            goodbye = "Game over"
        splash = graphics.Text(center, goodbye)
        splash.setFace("times roman")
        splash.setSize(36)  # The largest font size supported by graphics.py
        splash.setTextColor("red")
        splash.draw(self.win)
        try:
            self.get_key()
            self.close()
        except graphics.GraphicsError as e:
            # This happens when the close button is pressed.
            pass


class GridView(game_element.GameListener):
    """The grid of spaces in the game, displayed
    within a GameView.
    """

    def __init__(self, game: GameView, grid_size: int):
        """Square grid, with a little space
        around the tiles.
        Args:
           game: The surrounding GameView object
        """
        self.game = game
        self.win = game.win
        self.background = graphics.Rectangle(
            graphics.Point(0, 0), graphics.Point(game.width, game.height))
        self.background.setFill("wheat")
        self.background.draw(self.win)
        self.cell_width = (game.width - MARGIN) / grid_size
        self.tile_width = self.cell_width - MARGIN
        self.cell_height = (game.height - MARGIN) / grid_size
        self.tile_height = self.cell_height - MARGIN
        self.tiles = []
        # Initially empty tile spaces
        for row in range(grid_size):
            row_tiles = []
            for col in range(grid_size):
                ul, lr = self.tile_corners(row, col)
                tile_background = graphics.Rectangle(ul, lr)
                tile_background.setFill("grey")
                tile_background.setOutline("white")
                tile_background.draw(self.win)
                row_tiles.append(tile_background)
            self.tiles.append(row_tiles)

    def tile_corners(self, row: int, col: int) -> Tuple[graphics.Point, graphics.Point]:
        """upper left and lower right corners of tile at row,col"""
        ul_x = MARGIN + col * self.cell_width
        lr_x = ul_x + self.tile_width
        ul_y = MARGIN + row * self.cell_height
        lr_y = ul_y + self.tile_height
        ul = graphics.Point(ul_x, ul_y)
        lr = graphics.Point(lr_x, lr_y)
        return ul, lr

    def notify(self, event: game_element.GameEvent):
        """When a tile is created, we attach a new TileView
        to draw and redraw it as needed.
        """
        if event.kind == game_element.EventKind.tile_created:
            view = TileView(self, event.tile)
            event.tile.add_listener(view)
        else:
            raise Exception("Unexpected event: {}".format(event))


class TileView(object):
    """A Tile is the thing with a number that slides around the grid.
    A TileView is its graphic depiction.  The TileView object listens
    for events from the underlying Tile, and updates the depiction as
    needed.
    """

    def __init__(self, grid: GridView, tile: model.Tile):
        """Display the tile on the grid.
        Internally there are actually two graphics objects:
        A background rectangle and text within it. The
        background rectangle has a visible outline until
        the first time it moves.
        """
        self.grid = grid
        self.win = grid.win
        self.row = tile.row
        self.col = tile.col
        self.value = tile.value
        ul, lr = grid.tile_corners(self.row, self.col)
        background = graphics.Rectangle(ul, lr)
        background.setFill(RAMP[self.value])
        background.setOutline(TILE_OUTLINE_NEW)
        self.background = background
        cx = (ul.getX() + lr.getX()) / 2.0
        cy = (ul.getY() + lr.getY()) / 2.0
        center = graphics.Point(cx, cy)
        label = graphics.Text(center, str(self.value))
        label.setSize(36)
        self.label = label
        background.draw(self.win)
        label.draw(self.win)

    def slide_to(self, row, col):
        """Slide the tile to row,col"""
        ul_new, lr_new = self.grid.tile_corners(row, col)
        ul_old, lr_old = self.grid.tile_corners(self.row, self.col)
        self.row, self.col = row, col
        dx = (ul_new.getX() - ul_old.getX()) / ANIMATION_STEPS
        dy = (ul_new.getY() - ul_old.getY()) / ANIMATION_STEPS
        step_sleep = ANIMATION_TIME / ANIMATION_STEPS
        for step in range(ANIMATION_STEPS):
            self.background.setOutline(TILE_OUTLINE_OLD)
            self.background.move(dx, dy)
            self.label.move(dx, dy)
            time.sleep(step_sleep)

    def notify(self, event: game_element.GameEvent):
        """Receive notification of change from a tile.
        """
        if event.kind == game_element.EventKind.tile_updated:
            row, col = event.tile.row, event.tile.col
            if self.row != row or self.col != col:
                self.slide_to(row, col)
            if self.value != event.tile.value:
                self.value = event.tile.value
                tile_color = RAMP[event.tile.value]
                self.background.setFill(tile_color)
                self.label.setText(str(event.tile.value))
        elif event.kind == game_element.EventKind.tile_removed:
            self.label.undraw()
            self.background.undraw()
        else:
            raise Exception("Unexpected event {}".format(event))


if __name__ == "__main__":
    game_view = GameView(600, 600)
    grid_view = GridView(game_view, 4)
    grid = model.Board()
    grid.add_listener(grid_view)
    grid.place_tile()
    game_view.lose()
