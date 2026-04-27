import random
from collections import deque
from enum import Enum

from mecha.music.track import Track


class LoopMode(str, Enum):
    OFF = "off"
    SONG = "song"
    QUEUE = "queue"


class MusicQueue:
    def __init__(self) -> None:
        self._items: deque[Track] = deque()
        self.loop_mode = LoopMode.OFF

    def add(self, track: Track) -> None:
        self._items.append(track)

    def extend(self, tracks: list[Track]) -> None:
        self._items.extend(tracks)

    def next(self) -> Track | None:
        if not self._items:
            return None
        return self._items.popleft()

    def clear(self) -> None:
        self._items.clear()

    def append_left(self, track: Track) -> None:
        self._items.appendleft(track)

    def remove(self, position: int) -> Track:
        items = list(self._items)
        if position < 1 or position > len(items):
            raise IndexError(position)
        track = items.pop(position - 1)
        self._items = deque(items)
        return track

    def move(self, from_position: int, to_position: int) -> Track:
        items = list(self._items)
        if from_position < 1 or from_position > len(items):
            raise IndexError(from_position)
        if to_position < 1 or to_position > len(items):
            raise IndexError(to_position)
        track = items.pop(from_position - 1)
        items.insert(to_position - 1, track)
        self._items = deque(items)
        return track

    def shuffle(self) -> None:
        items = list(self._items)
        random.shuffle(items)
        self._items = deque(items)

    def append_finished_for_queue_loop(self, track: Track) -> None:
        self._items.append(track)

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __iter__(self):
        return iter(self._items)
