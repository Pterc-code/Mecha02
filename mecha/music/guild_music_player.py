import asyncio
import logging
from time import monotonic

import discord
from discord.ext import commands

from mecha.music.embeds import message_embed, track_embed
from mecha.music.errors import MusicError, PlaybackError, VoiceDisconnectedError
from mecha.music.playback import PlaybackFactory
from mecha.music.queue import LoopMode, MusicQueue
from mecha.music.source_resolver import SourceResolver
from mecha.music.track import ResolveResult, Track

log = logging.getLogger(__name__)


class GuildMusicPlayer:
    def __init__(self, bot: commands.Bot, guild_id: int, resolver: SourceResolver) -> None:
        self.bot = bot
        self.guild_id = guild_id
        self.resolver = resolver
        self.playback = PlaybackFactory(resolver.youtube)
        self.queue = MusicQueue()
        self.current: Track | None = None
        self.voice_client: discord.VoiceClient | None = None
        self.text_channel: discord.abc.Messageable | None = None
        self.status_message: discord.Message | None = None
        self.volume = 0.6
        self._current_source: discord.PCMVolumeTransformer | None = None
        self._play_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        self._skip_requested = False
        self._queue_changed = asyncio.Event()
        self._started_at: float | None = None
        self._stopping = False

    async def enqueue(self, result: ResolveResult, voice_channel: discord.VoiceChannel, text_channel) -> None:
        async with self._lock:
            self.text_channel = text_channel
            await self.ensure_voice(voice_channel)
            self.queue.extend(result.tracks)
            log.info(
                "Queued %s track(s) in guild %s from %s. Queue length is now %s.",
                len(result.tracks),
                self.guild_id,
                result.title,
                len(self.queue),
            )
            self._queue_changed.set()
            if self._play_task is None or self._play_task.done():
                self._stopping = False
                self._play_task = asyncio.create_task(self._play_loop(), name=f"music-player-{self.guild_id}")

    async def ensure_voice(self, voice_channel: discord.VoiceChannel) -> None:
        if self.voice_client is None:
            self.voice_client = voice_channel.guild.voice_client
        if self.voice_client and self.voice_client.is_connected():
            if self.voice_client.channel != voice_channel:
                await self.voice_client.move_to(voice_channel)
            return
        self.voice_client = await voice_channel.connect(timeout=20, reconnect=False)

    async def pause(self) -> None:
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()

    async def resume(self) -> None:
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()

    async def skip(self) -> None:
        log.info(
            "Skip requested in guild %s. Current=%s, remaining queue=%s, loop=%s.",
            self.guild_id,
            self.current.title if self.current else None,
            len(self.queue),
            self.queue.loop_mode.value,
        )
        if self.queue.loop_mode == LoopMode.SONG:
            self.current = None
        if self.voice_client and (self.voice_client.is_playing() or self.voice_client.is_paused()):
            self._skip_requested = True
            self.voice_client.stop()
        else:
            self._queue_changed.set()

    async def stop(self, disconnect: bool = True) -> None:
        await self.shutdown(disconnect=disconnect)

    async def shutdown(self, disconnect: bool = False) -> None:
        self._stopping = True
        self._queue_changed.set()
        self.queue.clear()
        self.current = None
        if self.voice_client:
            if self.voice_client.is_playing() or self.voice_client.is_paused():
                self.voice_client.stop()
            if disconnect and self.voice_client.is_connected():
                await self.voice_client.disconnect(force=False)
        self.voice_client = None

    def set_volume(self, value: float) -> None:
        self.volume = value
        if self._current_source:
            self._current_source.volume = value

    def progress_seconds(self) -> int | None:
        if self._started_at is None or self.current is None:
            return None
        return int(monotonic() - self._started_at)

    async def _play_loop(self) -> None:
        idle_timeout = self.bot.settings.music_idle_timeout_seconds
        while not self._stopping:
            track = self._next_track()
            if track is None:
                should_continue = await self._idle_disconnect(idle_timeout)
                if should_continue:
                    continue
                return

            self.current = track
            self._skip_requested = False
            try:
                await self._play_track(track)
            except VoiceDisconnectedError as error:
                log.info("Stopping music player in guild %s because voice disconnected: %s", self.guild_id, error)
                self.queue.clear()
                self.current = None
                self._started_at = None
                self._stopping = True
                return
            except MusicError as error:
                log.warning("Skipping failed track %s: %s", track.title, error)
                await self._send(message_embed("Skipped Track", f"{track.title}\n{error}", discord.Color.orange()))
            finally:
                if self.queue.loop_mode == LoopMode.QUEUE and self.current and not self._stopping:
                    self.queue.append_finished_for_queue_loop(self.current)
                if self.queue.loop_mode != LoopMode.SONG or self._skip_requested:
                    self.current = None
                    self._started_at = None

    def _next_track(self) -> Track | None:
        if self.queue.loop_mode == LoopMode.SONG and self.current and not self._skip_requested:
            return self.current
        return self.queue.next()

    async def _play_track(self, track: Track) -> None:
        if self.voice_client is None or not self.voice_client.is_connected():
            raise VoiceDisconnectedError("I am not connected to voice anymore.")

        log.info("Starting track in guild %s: %s <%s>", self.guild_id, track.title, track.url)
        self._current_source = await self.playback.create_source(track.url, self.volume)
        self._started_at = monotonic()
        await self._show_now_playing(track)

        done = asyncio.Event()

        def after_playback(error: Exception | None) -> None:
            if error:
                log.warning("Playback callback error: %s", error)
            self.bot.loop.call_soon_threadsafe(done.set)

        self.voice_client.play(self._current_source, after=after_playback)
        await done.wait()
        log.info("Track ended in guild %s: %s", self.guild_id, track.title)

    async def _show_now_playing(self, track: Track) -> None:
        embed = track_embed(track, "Now Playing", self.queue.loop_mode, len(self.queue))
        await self._send_or_edit_status(embed)

    async def _send_or_edit_status(self, embed: discord.Embed) -> None:
        if self.text_channel is None:
            return
        try:
            if self.status_message:
                await self.status_message.edit(embed=embed)
            else:
                self.status_message = await self.text_channel.send(embed=embed)
        except discord.HTTPException:
            self.status_message = await self.text_channel.send(embed=embed)

    async def _send(self, embed: discord.Embed) -> None:
        if self.text_channel is not None:
            await self.text_channel.send(embed=embed)

    async def _idle_disconnect(self, idle_timeout: int) -> bool:
        self.current = None
        self._started_at = None
        if idle_timeout > 0:
            self._queue_changed.clear()
            try:
                await asyncio.wait_for(self._queue_changed.wait(), timeout=idle_timeout)
            except asyncio.TimeoutError:
                pass
        if self.queue and not self._stopping:
            return True
        if self.voice_client and self.voice_client.is_connected() and not self.queue:
            await self.voice_client.disconnect(force=False)
            self.voice_client = None
            await self._send(message_embed("Disconnected", "Queue ended.", discord.Color.dark_grey()))
        return False
