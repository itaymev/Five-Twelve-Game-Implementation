"""
Board game element: Relates the model component
of a grid game to the view component.

Neither the game logic (in the model component)
nor the display logic (n the view component) is
defined here; this is the notification logic
for sending events from the model component
to the view component.

The 'model' component will inherit from the
GameListener class and generate EventKind events.
"""

from enum import Enum

class EventKind(Enum):
    """All the kinds of events that we may notify listeners of"""
    tile_created = 1
    tile_updated = 2
    tile_removed = 3


class GameEvent(object):
    """An event that may need to be depicted
    """
    def __init__(self, kind: EventKind,  tile: "Tile"):
        self.kind = kind
        self.tile = tile

    def __repr__(self):
        return f"GameEvent({self.kind}, {self.tile})"


class GameListener(object):
    """Abstract base class for objects that listen to
    game events in a model-view-controller pattern.
    Each listener must implement a 'notify' method.
    """
    def notify(self, event: GameEvent):
        raise NotImplementedError("Game Listener classes must implement 'notify'")

# -------------------------------------------


class GameElement(object):
    """Base class for game elements, especially to support
    depiction through Model-View-Controller.
    """

    def __init__(self):
        """Each game element can have zero or more listeners.
        Listeners are view components that react to notifications.
        """
        self._listeners = []

    def add_listener(self, listener: GameListener):
        self._listeners.append(listener)

    def notify_all(self, event: GameEvent):
        """Instead of handling graphics in the model component,
        we notify view components of each significant event and let
        the view component decide how to adjust the graphical view.
        When additional information must be packaged with an event,
        it goes in the optional 'data' parameter.
        """
        for listener in self._listeners:
            listener.notify(event)

