import base64
import asyncio
import logging
import re
import time

import aiohttp

from mecha.music.errors import ResolverError, SpotifyCredentialsError

log = logging.getLogger(__name__)


class SpotifyResolver:
    API_BASE = "https://api.spotify.com/v1"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    REQUEST_TIMEOUT_SECONDS = 15

    def __init__(self, client_id: str, client_secret: str, max_playlist_size: int) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.max_playlist_size = max_playlist_size
        self._access_token: str | None = None
        self._expires_at = 0.0

    def has_credentials(self) -> bool:
        return bool(self.client_id and self.client_secret)

    async def get_track(self, spotify_url: str) -> dict:
        track_id = self._extract_id(spotify_url, "track")
        return await self._get_json(f"{self.API_BASE}/tracks/{track_id}")

    async def get_playlist_tracks(self, spotify_url: str) -> tuple[str, list[dict], int]:
        playlist_id = self._extract_id(spotify_url, "playlist")
        playlist = await self._get_json(f"{self.API_BASE}/playlists/{playlist_id}")
        name = playlist.get("name") or "Spotify playlist"
        items = playlist.get("tracks", {}).get("items", [])
        next_url = playlist.get("tracks", {}).get("next")

        while next_url and len(items) < self.max_playlist_size:
            page = await self._get_json(next_url)
            items.extend(page.get("items", []))
            next_url = page.get("next")

        limited = items[: self.max_playlist_size]
        skipped_due_to_limit = max(0, (playlist.get("tracks", {}).get("total") or len(items)) - len(limited))
        tracks = [item.get("track") for item in limited if item and item.get("track")]
        return name, tracks, skipped_due_to_limit

    def search_query_for_track(self, track: dict) -> str:
        artists = " ".join(artist.get("name", "") for artist in track.get("artists", []))
        return f"{track.get('name', '')} {artists} official audio".strip()

    def metadata_from_track(self, track: dict) -> dict:
        album = track.get("album") or {}
        images = album.get("images") or []
        return {
            "title": track.get("name") or "Spotify track",
            "artist": ", ".join(artist.get("name", "") for artist in track.get("artists", [])),
            "album": album.get("name"),
            "duration": int((track.get("duration_ms") or 0) / 1000) or None,
            "thumbnail": images[0]["url"] if images else None,
            "original_url": track.get("external_urls", {}).get("spotify"),
        }

    async def _get_json(self, url: str) -> dict:
        if not self.has_credentials():
            raise SpotifyCredentialsError(
                "Spotify links require `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` in `.env`."
            )

        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        timeout = aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT_SECONDS)
        try:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 404:
                        raise ResolverError("I could not find that Spotify item.")
                    if response.status in {401, 403}:
                        raise ResolverError("Spotify rejected access to that item. It may be private or unavailable.")
                    if response.status >= 400:
                        text = await response.text()
                        log.warning("Spotify request failed: %s %s", response.status, text)
                        raise ResolverError("Spotify metadata lookup failed.")
                    return await response.json()
        except asyncio.TimeoutError as error:
            raise ResolverError("Spotify took too long to respond.") from error
        except aiohttp.ClientError as error:
            log.warning("Spotify request error: %s", error)
            raise ResolverError("Spotify metadata lookup failed.") from error

    async def _get_access_token(self) -> str:
        if self._access_token and time.time() < self._expires_at:
            return self._access_token

        credentials = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        headers = {"Authorization": "Basic " + base64.b64encode(credentials).decode("ascii")}
        data = {"grant_type": "client_credentials"}

        timeout = aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT_SECONDS)
        try:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                async with session.post(self.TOKEN_URL, data=data) as response:
                    if response.status >= 400:
                        raise SpotifyCredentialsError("Spotify credentials were rejected.")
                    payload = await response.json()
        except asyncio.TimeoutError as error:
            raise ResolverError("Spotify took too long to respond.") from error
        except aiohttp.ClientError as error:
            log.warning("Spotify token request error: %s", error)
            raise ResolverError("Spotify authentication failed.") from error

        self._access_token = payload["access_token"]
        self._expires_at = time.time() + int(payload.get("expires_in", 3600)) - 60
        return self._access_token

    @staticmethod
    def _extract_id(value: str, kind: str) -> str:
        patterns = [
            rf"open\.spotify\.com/{kind}/([A-Za-z0-9]+)",
            rf"spotify:{kind}:([A-Za-z0-9]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, value)
            if match:
                return match.group(1)
        raise ResolverError(f"That does not look like a Spotify {kind} link.")
