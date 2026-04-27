import asyncio
import logging
from urllib.parse import parse_qs, urlparse

import yt_dlp

from mecha.music.errors import ResolverError
from mecha.music.track import ResolveResult, Track

log = logging.getLogger(__name__)


class YouTubeResolver:
    REQUEST_TIMEOUT_SECONDS = 30

    def __init__(self, max_playlist_size: int) -> None:
        self.max_playlist_size = max_playlist_size

    async def resolve(self, query_or_url: str, requester) -> ResolveResult:
        if self._looks_like_playlist(query_or_url):
            return await self.resolve_playlist(query_or_url, requester)
        if self._looks_like_url(query_or_url):
            return await self.resolve_video(query_or_url, requester, "youtube")
        return await self.search(query_or_url, requester)

    async def resolve_video(self, url: str, requester, source_type: str = "youtube") -> ResolveResult:
        info = await self._extract(url, extract_flat=False)
        if "entries" in info and info["entries"]:
            entry = info["entries"][0]
        else:
            entry = info
        track = self._track_from_info(entry, requester, source_type, original_url=url)
        return ResolveResult([track], track.title, source_type)

    async def resolve_playlist(self, url: str, requester) -> ResolveResult:
        playlist_url = self._canonical_playlist_url(url)
        info = await self._extract(playlist_url, extract_flat=True)
        entries = list(info.get("entries") or [])[: self.max_playlist_size]
        tracks: list[Track] = []
        skipped = 0

        for entry in entries:
            if not entry:
                skipped += 1
                continue
            try:
                if not self._is_video_like(entry):
                    raise ResolverError("Playlist entry was not a video.")
                tracks.append(self._track_from_info(entry, requester, "youtube", playlist_url=playlist_url))
            except ResolverError:
                skipped += 1

        if not tracks:
            if self._looks_like_watch_playlist_url(url):
                return await self.resolve_video(self._strip_playlist_from_watch_url(url), requester, "youtube")
            raise ResolverError("I could not find playable videos in that YouTube playlist.")

        return ResolveResult(
            tracks=tracks,
            title=info.get("title") or "YouTube playlist",
            source="youtube",
            skipped=skipped,
            is_playlist=True,
        )

    async def search(self, query: str, requester, source_type: str = "search", original_url: str | None = None) -> ResolveResult:
        info = await self._extract(f"ytsearch5:{query}", extract_flat=True)
        entries = info.get("entries") or []
        for entry in entries:
            if self._is_video_like(entry):
                track = self._track_from_info(entry, requester, source_type, original_url=original_url)
                return ResolveResult([track], track.title, source_type)
        raise ResolverError("I could not find a playable YouTube video for that search.")

    async def get_stream_url(self, url: str) -> str:
        info = await self._extract(url, extract_flat=False)
        return info["url"]

    async def _extract(self, query: str, extract_flat: bool):
        def run_extract():
            options = {
                "format": "bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "extract_flat": extract_flat,
                "noplaylist": not extract_flat,
                "default_search": "ytsearch",
                "source_address": "0.0.0.0",
                "socket_timeout": 15,
            }
            with yt_dlp.YoutubeDL(options) as ydl:
                return ydl.extract_info(query, download=False)

        try:
            return await asyncio.wait_for(asyncio.to_thread(run_extract), timeout=self.REQUEST_TIMEOUT_SECONDS)
        except asyncio.TimeoutError as error:
            raise ResolverError("YouTube took too long to respond.") from error
        except yt_dlp.utils.DownloadError as error:
            log.warning("YouTube extraction failed for %s: %s", query, error)
            raise ResolverError("I could not resolve that YouTube item.") from error

    def _track_from_info(
        self,
        info: dict,
        requester,
        source_type: str,
        original_url: str | None = None,
        playlist_url: str | None = None,
    ) -> Track:
        video_id = info.get("id")
        url = info.get("webpage_url") or info.get("url")
        if playlist_url and video_id:
            url = f"https://www.youtube.com/watch?v={video_id}"
        elif video_id and (not url or not str(url).startswith("http")):
            url = f"https://www.youtube.com/watch?v={video_id}"
        if not url:
            raise ResolverError("A playlist item did not include a playable URL.")
        if self._is_playlist_url(url):
            raise ResolverError("YouTube result was a playlist, not a video.")

        return Track(
            title=info.get("title") or "Unknown title",
            url=url,
            source_type=source_type,
            duration=info.get("duration"),
            requester=requester,
            thumbnail=info.get("thumbnail"),
            original_url=original_url if original_url != url else None,
            playlist_url=playlist_url,
        )

    @staticmethod
    def _looks_like_url(value: str) -> bool:
        return value.startswith("http://") or value.startswith("https://")

    @staticmethod
    def _looks_like_playlist(value: str) -> bool:
        return "list=" in value or "/playlist" in value

    @staticmethod
    def _looks_like_watch_playlist_url(value: str) -> bool:
        parsed = urlparse(value)
        return parsed.path == "/watch" and "list" in parse_qs(parsed.query)

    @staticmethod
    def _canonical_playlist_url(value: str) -> str:
        parsed = urlparse(value)
        list_id = parse_qs(parsed.query).get("list", [None])[0]
        if list_id:
            return f"https://www.youtube.com/playlist?list={list_id}"
        return value

    @staticmethod
    def _strip_playlist_from_watch_url(value: str) -> str:
        parsed = urlparse(value)
        video_id = parse_qs(parsed.query).get("v", [None])[0]
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return value

    @staticmethod
    def _is_playlist_url(value: str) -> bool:
        return "/playlist" in value or ("list=" in value and "watch?v=" not in value)

    def _is_video_like(self, info: dict | None) -> bool:
        if not info:
            return False
        if info.get("_type") == "playlist":
            return False
        ie_key = str(info.get("ie_key") or "").lower()
        if "playlist" in ie_key or "tab" in ie_key:
            return False
        url = str(info.get("webpage_url") or info.get("url") or "")
        if url and self._is_playlist_url(url):
            return False
        return bool(info.get("id") or url)
