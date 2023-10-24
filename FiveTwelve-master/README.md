# FiveTwelve

FiveTwelve is a sliding tile game based on 2048,
with a few changes.  2048 was itself based on an
earlier game called 1024, which
was inspired by the more challenging
sliding tile game Threes.

## Game Play

The game is played on a 4x4 grid. Initially tiles containing the value 2 are placed randomly on the grid.  In each turn, the player may move all the tiles left, right, up, or down.  Tiles will slide as far as possible in the indicated direction, stopping when they reach an edge of the grid or when they meet a tile with a different value.  If a tile meets another tile with the same value, it absorbs the other tile (adding the value of the other tile to its own, thereby doubling), and *continues moving*.

The order of movement matters when more than one merge is possible.  Consider a move *right* in the following row:

```text
2 4 4 4
```

Should this produce

```text
_ 2 4 8
```

or

```text
_ 2 8 4
```

? The rule is that the rightmost tile moves first for a move right, the leftmost tile moves first for a move left, etc., so this move produces

```text
_ 2 4 8
```

After each move, a new tile with value 2 is placed in a random open square on the grid.  When there is no open square to place the new tile, the game is over and the player's score is the sum of all tiles on the board.

## Differences from 2048

The game play should be familiar to those who have played 2048, but there are a few differences.

* Cascading merges:  In 2048, a tile may merge with another tile at most once in one turn.
  In FiveTwelve, a tile stops when it absorbs another,
   but it can then be absorbed by another tile.  Thus, if we start with
   ```4 2 2 8```
   and we are moving right, the sequence is
  * The 8 tries to slide right.  It is stuck against the edge.
  * The rightmost 2 tries to slide right.  It is stuck against the 8.
  * The next 2 tries to slide right.  It meets the 2 to its right
  and absorbs it, becoming a 4. Now we have ```4 _ 4 8```
  * The leftmost 4 slides right until it meets the 4 that was
    just created by merging 2s.  It absorbs the new 4 and
    becomes an 8. We end up with ```_ _ 8 8```

* Ineffective moves are permitted.  Consider the board

```text
   2 4 8 16
   2 4 8 16
   _ _ 8 16
   _ _ 8 16
```

The player may choose to slide the tiles right, but no tile can move farther to the right.  In 2048, this move is not allowed (the player must choose a different direction).  In FiveTwelve, the move right is allowed, and has no effect except to cause a new tile with value 2 to be introduced in one of the empty spaces.

* You can never win.  Because FiveTwelve is like life.  You just keep adding to your score until gameplay ends.

## Known bugs and limitations

* You must click the FiveTwelve window with a pointing device to send keystrokes to the game.

## Implementation notes: MVC

FiveTwelve follows a Model-View-Controller (MVC) organization or *design pattern*.   The model component (model.py) contains all the game logic and data structures.  The model component has no direct dependencies on the view or controller components, but each element of the model component permits registration of *listeners* and announces significant events to its listeners.

The view component is responsible for maintaining the visual representation of the game.  Most objects in the model component have peer objects (with a related class name) in the view component. The view objects are registered as *listeners* on their model component peers. They receive notifications of changes to the model, and make corresponding changes to the visual representation.

The view component depends on (and imports) the model component.  View objects may inspect their peer model objects (e.g., obtaining the current value of a tile, or its current position).  The model component does not depend on the view component, does not import it, and will operate the same with zero views, one view, or multiple views.

The *controller* part of the Model-View-Controller organization is currently combined with the main program in game_manager.py, with keystroke acquisition in keypress.py.  The controller depends on both the the model and view componments, and makes the initial connection bertween

The current view component uses Zelle's graphics module (graphics/graphics.py), which in turn uses the TkInter graphics module that is included in Python distributions.  Keypress.py also depends on graphics.py, and thereby on TkInter.  A version of FiveTwelve that uses PyQt, PyGame, or another graphics/GUI layer will require an implementation of modules providing the same API as view.py and keypress.py.  It should be possible to make minimal changes to game_controller.py (just importing the different view modules) and no changes at all to model.py.

Most changes to game logic in model.py should also be possible without changing view.py. For example, adopting the 2048 rule regarding merging (only one merge per tile per move) should require no change to view.py.  Adopting the 2048 rule regarding ineffective moves would require small changes to model.py and controller.py but no change to view.py or keypress.py.  This independence is the point of MVC organization.

## What students must program

Although there is a lot of code to add to the skeleton, a fair amount of it is given to
you in [the HOWTO document](doc/HOWTO.md).  The main thing you have to design
on your own are the loops that move each tile in turn, in the correct order.
