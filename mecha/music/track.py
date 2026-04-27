from dataclasses import dataclass

import discord


@dataclass(slots=True)
class Track:
    title: str
    url: str
    source_type: str
    duration: int | None = None
    requester: discord.abc.User | discord.Member | None = None
    thumbnail: str | None = None
    original_url: str | None = None
    artist: str | None = None
    album: str | None = None
    playlist_url: str | None = None

    @property
    def display_url(self) -> str:
        return self.original_url or self.url


@dataclass(slots=True)
class ResolveResult:
    tracks: list[Track]
    title: str
    source: str
    skipped: int = 0
    is_playlist: bool = False
