"""
Tests for model.py.

Note that the unittest module predates PEP-8 guidelines, which
is why we have a bunch of names that don't comply with the
standard.
"""
import sys

from model import Vec, Board, Tile
import unittest

def board_diff(actual: Board, expected: Board):
    """Print actual and expected board side-by-side."""
    print(f"\nActual\t\t\tExpected", file=sys.stderr)
    for row in range(len(expected)):
            print(f"{actual[row]} \t {expected[row]} ", file=sys.stderr)
    print(file=sys.stderr)

class TestVec(unittest.TestCase):

    def test_equality(self):
        v1 = Vec(7, 12)
        v2 = Vec(8, 13)
        self.assertNotEqual(v1, v2)
        v3 = Vec(7, 12)
        self.assertEqual(v1, v3)

    def test_addition(self):
        v1 = Vec(8, 7)
        v2 = Vec(12, 15)
        self.assertEqual(v1 + v2, Vec(20, 22))
        # Addition does not modify the points that have been added
        self.assertEqual(v1, Vec(8, 7))
        self.assertEqual(v2, Vec(12, 15))


class TestBoardConstructor(unittest.TestCase):

    def test_default(self):
        board = Board()
        self.assertEqual(board.tiles, [[None, None, None, None],
                                       [None, None, None, None],
                                       [None, None, None, None],
                                       [None, None, None, None]])

    def test_3x5(self):
        board = Board(rows=3, cols=5)
        self.assertEqual(board.tiles, [[None, None, None, None, None],
                                       [None, None, None, None, None],
                                       [None, None, None, None, None]])

    def test_constructed_empties(self):
        """A newly constructed Board should always have at least
        one empty space.
        """
        board = Board()
        self.assertTrue(board.has_empty())


class TestScaffolding(unittest.TestCase):

    def test_to_from_list(self):
        """to_list and from_list should be inverse"""
        board = Board()
        as_list = [[0, 2, 2, 4], [2, 0, 2, 8], [8, 2, 2, 4], [4, 2, 2, 0]]
        board.from_list(as_list)
        self.assertEqual(board.to_list(), as_list)

    def test_from_to(self):
        """to_list and from_list should be inverse"""
        board = Board()
        board.place_tile()
        board.place_tile(value=32)
        board.place_tile()
        as_list = board.to_list()
        board.from_list(as_list)
        again = board.to_list()
        self.assertEqual(as_list, again)


class TestBoundsCheck(unittest.TestCase):

    def test_bounds_default_shape(self):
        board = Board()
        self.assertTrue(board.in_bounds(Vec(0, 0)))
        self.assertTrue(board.in_bounds(Vec(3, 3)))
        self.assertTrue(board.in_bounds(Vec(1, 2)))
        self.assertTrue(board.in_bounds(Vec(0, 3)))
        self.assertFalse(board.in_bounds(Vec(-1, 0)))  # off the top
        self.assertFalse(board.in_bounds(Vec(1, -1)))  # off the left
        self.assertFalse(board.in_bounds(Vec(4, 3)))  # off the bottom
        self.assertFalse(board.in_bounds(Vec(1, 4)))  # off the right

    def test_bounds_odd_shape(self):
        """Non-square board to make sure we're using row and column
        correctly.
        """
        board = Board(rows=2, cols=4)
        self.assertTrue(board.in_bounds(Vec(0, 0)))
        self.assertTrue(board.in_bounds(Vec(1, 3)))
        self.assertFalse(board.in_bounds(Vec(3, 1)))


class TestSlide(unittest.TestCase):

    def test_slide_left_to_edge(self):
        """A tile should stop just when it reaches the edge"""
        board = Board()
        board.from_list([[0, 0, 0, 0],
                         [0, 0, 2, 0],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0]])
        board.slide(Vec(1, 2), Vec(0, -1))  # Slide the 2 left
        self.assertEqual(board.to_list(),
                         [[0, 0, 0, 0],
                          [2, 0, 0, 0],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0]])

    def test_slide_right_to_edge(self):
        """A tile should stop just when it reaches the edge"""
        board = Board()
        board.from_list([[0, 0, 0, 0],
                         [0, 0, 2, 0],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0]])
        board.slide(Vec(1, 2), Vec(0, 1))  # Slide the 2 right
        self.assertEqual(board.to_list(),
                         [[0, 0, 0, 0],
                          [0, 0, 0, 2],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0]])

    def test_slide_already_at_edge(self):
        """A tile already at the edge can't slide farther that way"""
        board = Board()
        board.from_list([[0, 0, 0, 0],
                         [0, 0, 0, 4],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0]])
        board.slide(Vec(1, 3), Vec(0, 1))  # To the right
        self.assertEqual(board.to_list(),
                         [[0, 0, 0, 0],
                          [0, 0, 0, 4],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0]])

    def test_empty_wont_slide(self):
        """Sliding an empty position has no effect"""
        board = Board()
        board.from_list([[2, 0, 0, 0],
                         [0, 2, 0, 0],
                         [0, 0, 2, 0],
                         [0, 0, 0, 2]])
        board.slide(Vec(1, 0), Vec(0, 1))  # Space 1,0 is empty
        self.assertEqual(board.to_list(),
                         [[2, 0, 0, 0],
                          [0, 2, 0, 0],
                          [0, 0, 2, 0],
                          [0, 0, 0, 2]])

    def test_slide_into_obstacle(self):
        """A tile should stop when it reaches another tile"""
        board = Board()
        board.from_list([[2, 0, 0, 0],
                         [0, 2, 4, 0],
                         [0, 0, 2, 0],
                         [0, 0, 0, 2]])
        board.slide(Vec(1, 1), Vec(0, 1))  # Space 1,0 is empty
        self.assertEqual(board.to_list(),
                         [[2, 0, 0, 0],
                          [0, 2, 4, 0],
                          [0, 0, 2, 0],
                          [0, 0, 0, 2]])

    def test_slide_merge(self):
        """Equal tiles merge when they meet"""
        board = Board()
        board.from_list([[2, 0, 0, 0],
                         [0, 2, 2, 4],
                         [0, 0, 2, 0],
                         [0, 0, 0, 2]])
        board.slide(Vec(1, 1), Vec(0, 1))
        self.assertEqual(board.to_list(),
                         [[2, 0, 0, 0],
                          [0, 0, 4, 4],
                          [0, 0, 2, 0],
                          [0, 0, 0, 2]])

    def test_move_merge_up(self):
        board = Board()
        board.from_list([[4, 0, 2, 2],
                         [2, 0, 2, 2],
                         [2, 2, 4, 0],
                         [2, 2, 2, 2]])
        board.up()
        expected = [[4, 4, 8, 4],
                    [4, 0, 4, 2],
                    [2, 0, 2, 0],
                    [0, 0, 0, 0]]
        actual = board.to_list()
        board_diff(actual, expected)
        self.assertEqual(actual, expected)


class TestMove(unittest.TestCase):
    """The moves are 'right', 'left', 'up', 'down'.
    These methods are normally called from the 'keypress.py' module.
    """

    def test_move_all_right(self):
        """Simple slide with no merges"""
        board = Board()
        board.from_list([[2, 0, 0, 0],
                         [0, 2, 0, 0],
                         [0, 0, 2, 0],
                         [0, 0, 0, 2]])
        board.right()
        self.assertEqual(board.to_list(),
                         [[0, 0, 0, 2],
                          [0, 0, 0, 2],
                          [0, 0, 0, 2],
                          [0, 0, 0, 2]])

    def test_move_all_left(self):
        """Simple slide with no merges"""
        board = Board()
        board.from_list([[2, 0, 0, 0],
                         [0, 2, 0, 0],
                         [0, 0, 2, 0],
                         [0, 0, 0, 2]])
        board.left()
        self.assertEqual(board.to_list(),
                         [[2, 0, 0, 0],
                          [2, 0, 0, 0],
                          [2, 0, 0, 0],
                          [2, 0, 0, 0]])

    def test_move_all_up(self):
        """Simple slide with no merges"""
        board = Board()
        board.from_list([[2, 0, 0, 0],
                         [0, 2, 0, 0],
                         [0, 0, 2, 0],
                         [0, 0, 0, 2]])
        board.up()
        self.assertEqual(board.to_list(),
                         [[2, 2, 2, 2],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0]])

    def test_move_merge_right(self):
        board = Board()
        board.from_list([[2, 0, 2, 0],
                         [2, 2, 2, 0],
                         [2, 2, 0, 0],
                         [2, 2, 2, 2]])
        board.right()
        self.assertEqual(board.to_list(),
                         [[0, 0, 0, 4],
                          [0, 0, 2, 4],  # Must work from right to left
                          [0, 0, 0, 4],
                          [0, 0, 4, 4]])  # Tile stops sliding when it merges

    def test_move_merge_up(self):
        board = Board()
        board.from_list([[4, 0, 2, 2],
                         [2, 0, 2, 2],
                         [2, 2, 4, 0],
                         [2, 2, 2, 2]])
        board.up()
        expected = [[4, 4, 8, 4],
                    [4, 0, 2, 2],
                    [2, 0, 0, 0],
                    [0, 0, 0, 0]]
        actual = board.to_list()
        # board_diff(actual, expected)
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
