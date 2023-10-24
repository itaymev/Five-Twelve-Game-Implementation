"""
The game state and logic (model component) of 512, 
a game based on 2048 with a few changes. 
This is the 'model' part of the model-view-controller
construction plan.  It must NOT depend on any
particular view component, but it produces event 
notifications to trigger view updates. 
"""

from game_element import GameElement, GameEvent, EventKind
from typing import List, Tuple, Optional
import random

# Configuration constants
GRID_SIZE = 4

class Vec():
    """A Vec is an (x,y) or (row, column) pair that
    represents distance along two orthogonal axes.
    Interpreted as a position, a Vec represents
    distance from (0,0).  Interpreted as movement,
    it represents distance from another position.
    Thus we can add two Vecs to get a Vec.
    """
    #Fixme:  We need a constructor, and __add__ method, and __eq__.
    def __init__(self, row: int, column: int) -> "Vec":
        self.row = row
        self.column = column

    def __add__(self, other: "Vec") -> "Vec":
        new_row = self.row + other.row
        new_column = self.column + other.column
        return Vec(new_row, new_column)

    def __sub__(self, other: "Vec") -> "Vec":
        new_row = self.row - other.row
        new_column = self.column - other.column
        return Vec(new_row, new_column)

    def __eq__(self, other: "Vec") -> bool:
        return self.row == other.row and self.column == other.column


class Tile(GameElement):
    """A slidy numbered thing."""

    def __init__(self, pos: Vec, value: int):
        super().__init__()
        self.row = pos.row
        self.col = pos.column
        self.value = value

    def __repr__(self):
        """Not like constructor --- more useful for debugging"""
        return f"Tile[{self.row},{self.col}]:{self.value}"

    def __str__(self):
        return str(self.value)

    def move_to(self, new_pos: Vec):
        self.row = new_pos.row
        self.col = new_pos.column
        self.notify_all(GameEvent(EventKind.tile_updated, self))

    def __eq__(self, other: "Tile"):
        return self.value == other.value

    # def merge(self, other: "Tile"):
    #     self.value = self.value + other.value

    def merge(self, other: "Tile"):
        # This tile incorporates the value of the other tile
        self.value = self.value + other.value
        self.notify_all(GameEvent(EventKind.tile_updated, self))
        # The other tile has been absorbed.  Resistance was futile.
        other.notify_all(GameEvent(EventKind.tile_removed, other))


class Board(GameElement):
    """The game grid.  Inherits 'add_listener' and 'notify_all'
    methods from game_element.GameElement so that the game
    can be displayed graphically.
    """

    # FIXME: a grid holds a matrix of tiles

    def __init__(self, rows=4, cols=4):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.tiles = [ ]
        for row in range(rows):
            row_tiles = [ ]
            for col in range(cols):
                row_tiles.append(None)
            self.tiles.append(row_tiles)

    def __getitem__(self, pos: Vec) -> Tile:
        return self.tiles[pos.row][pos.column]

    def __setitem__(self, pos: Vec, tile: Tile):
        self.tiles[pos.row][pos.column] = tile

    def _empty_positions(self) -> List[Vec]:
        """Return a list of positions of None values,
        i.e., unoccupied spaces.
        """
        empty_list = []
        for row in range(self.rows):
            for col in range(self.cols):
                vec = Vec(row, col)
                if self.__getitem__(vec) is None:
                    empty_list.append(vec)
        return empty_list

    def has_empty(self) -> bool:
        """Is there at least one grid element without a tile?"""
        return len(self._empty_positions()) > 0
        # FIXME: Should return True if there is some element with value None

    def place_tile(self, value=None):
        """Place a tile on a randomly chosen empty square."""
        empties = self._empty_positions()
        assert len(empties) > 0
        choice = random.choice(empties)
        row, col = choice.row, choice.column
        if value is None:
            # 0.1 probability of 4
            if random.random() > 0.1:
                value = 2
            else:
                value = 4
        new_tile = Tile(Vec(row, col), value)
        self.tiles[row][col] = new_tile
        self.notify_all((GameEvent(EventKind.tile_created, new_tile)))

    def score(self) -> int:
        """Calculate a score from the board.
        (Differs from classic 1024, which calculates score
        based on sequence of moves rather than state of
        board.
        """
        score = 0
        listed = self.to_list()
        for l in listed:
            score += sum(l)
        return score

    def to_list(self) -> List[List[int]]:
        """Test scaffolding: represent each Tile by its
        integer value and empty positions as 0
        """
        result = [ ]
        for row in self.tiles:
            row_values = []
            for col in row:
                if col is None:
                    row_values.append(0)
                else:
                    row_values.append(col.value)
            result.append(row_values)
        return result

    # SHOULD THIS RETURN List[List[Tile]] INSTEAD???
    def from_list(self, values: List[List[int]]) -> List[List]:
        """Test scaffolding: set board tiles to the
        given values, where 0 represents an empty space.
        """
        # self.rows = len(values)
        # self.cols = len(values[0])

        for i in range(len(values)):
            for j in range(len(values[i])):
                if values[i][j] == 0:
                    self.tiles[i][j] = None
                else:
                    value = values[i][j]
                    new_tile = Tile(Vec(i, j), value)
                    self.tiles[i][j] = new_tile
        # print(self.tiles)
        return self.tiles

    def in_bounds(self, pos: Vec) -> bool:
        """Is position (pos.x, pos.y) a legal position on the board?"""
        return (pos.row >= 0 and pos.row < self.rows) and (pos.column >= 0 and pos.column < self.cols)

    def _move_tile(self, old_pos: Vec, new_pos: Vec):
        # You write this
        # if self[new_pos] is None or self[old_pos] == self[new_pos]:
        #     self[old_pos].move_to(new_pos)
        # print(f'old, new: {self[old_pos]}, {self[new_pos]}')
        # print(f'old_pos: {old_pos.row}, {old_pos.column}')
        # print(f'new_pos: {new_pos.row}, {new_pos.column}')
        self[old_pos].move_to(new_pos)
        self[new_pos] = self[old_pos]
        self[old_pos] = None

    def slide(self, pos: Vec, dir: Vec):
        """Slide tile at row,col (if any)
        in direction (dx,dy) until it bumps into
        another tile or the edge of the board.
        """
        if self[pos] is None:
            return
        while True:
            new_pos = pos + dir
            # print(new_pos)
            if not self.in_bounds(new_pos):
                # print('In out of bounds, breaking out.')
                break
            # print(f'value of self[new_pos]: {self[new_pos]}')
            if self[new_pos] is None:
                # print('self[new_pos] is None')
                self._move_tile(pos, new_pos)
            elif self[pos] == self[new_pos]:
                # print('merge')
                self[pos].merge(self[new_pos])
                self._move_tile(pos, new_pos)
                break  # Stop moving when we merge with another tile
            else:
                # Stuck against another tile
                # print('stuck against another tile')
                break
            pos = new_pos

    def original_left(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.slide(Vec(row, col), Vec(0, -1))

    def original_right(self):
        for row in range(self.rows):
            for col in range(self.cols - 1, -1, -1):
                self.slide(Vec(row, col), Vec(0, 1))

    def original_up(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.slide(Vec(row, col), Vec(-1, 0))

    def original_down(self):
        for row in range(self.rows - 1, -1, -1):
            for col in range(self.cols):
                self.slide(Vec(row, col), Vec(1, 0))

    def _move(self, start_pos: Vec, direction: Vec, how_to_next_pos: Vec, how_to_next_row: Vec):
        start_col = start_pos.column
        for row in range(self.rows):
            for col in range(self.cols):
                self.slide(start_pos, direction)
                start_pos += how_to_next_pos
            start_pos.column = start_col
            start_pos += how_to_next_row

    def left(self):
        self._move(Vec(0, 0), Vec(0, -1), Vec(0, 1), Vec(1, 0))

    def right(self):
        self._move(Vec(0, self.cols - 1), Vec(0, 1), Vec(0, -1), Vec(1, 0))

    def up(self):
        self._move(Vec(0, 0), Vec(-1, 0), Vec(0, 1), Vec(1, 0))

    def down(self):
        self._move(Vec(self.rows - 1, 0), Vec(1, 0), Vec(0, 1), Vec(-1, 0))
