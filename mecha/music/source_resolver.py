import logging
from urllib.parse import urlparse

from mecha.music.constants import SPOTIFY_DOMAINS, YOUTUBE_DOMAINS
from mecha.music.errors import ResolverError
from mecha.music.spotify_resolver import SpotifyResolver
from mecha.music.track import ResolveResult
from mecha.music.youtube_resolver import YouTubeResolver

log = logging.getLogger(__name__)


class SourceResolver:
    def __init__(self, youtube: YouTubeResolver, spotify: SpotifyResolver) -> None:
        self.youtube = youtube
        self.spotify = spotify

    async def resolve(self, query_or_url: str, requester) -> ResolveResult:
        value = query_or_url.strip()
        if not value:
            raise ResolverError("Tell me what to play.")

        kind = self.detect(value)
        if kind == "youtube":
            return await self.youtube.resolve(value, requester)
        if kind == "spotify_track":
            return await self._resolve_spotify_track(value, requester)
        if kind == "spotify_playlist":
            return await self._resolve_spotify_playlist(value, requester)
        if kind == "url":
            raise ResolverError("I only support YouTube and Spotify links.")
        return await self.youtube.search(value, requester)

    def detect(self, value: str) -> str:
        if value.startswith("spotify:track:"):
            return "spotify_track"
        if value.startswith("spotify:playlist:"):
            return "spotify_playlist"
        if not value.startswith(("http://", "https://")):
            return "search"

        parsed = urlparse(value)
        host = parsed.netloc.lower()
        if host in YOUTUBE_DOMAINS or host.endswith(".youtube.com"):
            return "youtube"
        if host in SPOTIFY_DOMAINS and "/track/" in parsed.path:
            return "spotify_track"
        if host in SPOTIFY_DOMAINS and "/playlist/" in parsed.path:
            return "spotify_playlist"
        return "url"

    async def _resolve_spotify_track(self, value: str, requester) -> ResolveResult:
        spotify_track = await self.spotify.get_track(value)
        track = await self._resolve_spotify_track_data(spotify_track, requester, value)
        return ResolveResult([track], track.title, "spotify_resolved")

    async def _resolve_spotify_track_data(self, spotify_track: dict, requester, fallback_url: str):
        metadata = self.spotify.metadata_from_track(spotify_track)
        result = await self.youtube.search(
            self.spotify.search_query_for_track(spotify_track),
            requester,
            "spotify_resolved",
            metadata["original_url"] or fallback_url,
        )
        track = result.tracks[0]
        track.title = metadata["title"]
        track.artist = metadata["artist"]
        track.album = metadata["album"]
        track.duration = metadata["duration"] or track.duration
        track.thumbnail = metadata["thumbnail"] or track.thumbnail
        track.original_url = metadata["original_url"] or fallback_url
        return track

    async def _resolve_spotify_playlist(self, value: str, requester) -> ResolveResult:
        playlist_name, spotify_tracks, skipped = await self.spotify.get_playlist_tracks(value)
        tracks = []
        for spotify_track in spotify_tracks:
            if spotify_track.get("is_local"):
                log.warning("Skipped local Spotify playlist track %s", spotify_track.get("name", "unknown"))
                skipped += 1
                continue
            try:
                tracks.append(await self._resolve_spotify_track_data(spotify_track, requester, value))
            except ResolverError as error:
                log.warning(
                    "Skipped Spotify playlist track %s: %s",
                    spotify_track.get("name", "unknown"),
                    error,
                )
                skipped += 1

        if not tracks:
            raise ResolverError("I could not resolve any Spotify playlist tracks to YouTube.")

        return ResolveResult(
            tracks=tracks,
            title=playlist_name,
            source="spotify_resolved",
            skipped=skipped,
            is_playlist=True,
        )
