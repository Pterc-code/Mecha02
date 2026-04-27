import discord

from mecha.music.constants import QUEUE_PAGE_SIZE
from mecha.music.queue import LoopMode, MusicQueue
from mecha.music.track import ResolveResult, Track
from mecha.utils.format_time import format_time


def track_embed(track: Track, title: str, loop_mode: LoopMode, queue_length: int, progress: int | None = None) -> discord.Embed:
    embed = discord.Embed(title=title, description=f"[{track.title}]({track.url})", color=discord.Color.blurple())
    embed.add_field(name="Requester", value=track.requester.mention if track.requester else "unknown", inline=True)
    embed.add_field(name="Duration", value=format_time(track.duration), inline=True)
    embed.add_field(name="Source", value=track.source_type, inline=True)
    embed.add_field(name="Loop", value=loop_mode.value, inline=True)
    embed.add_field(name="Queue", value=str(queue_length), inline=True)
    if track.artist:
        embed.add_field(name="Artist", value=track.artist, inline=True)
    if track.playlist_url:
        embed.add_field(name="From Playlist", value="[Open playlist](" + track.playlist_url + ")", inline=True)
    if progress is not None:
        embed.add_field(name="Progress", value=f"{format_time(progress)} / {format_time(track.duration)}", inline=True)
    if track.thumbnail:
        embed.set_thumbnail(url=track.thumbnail)
    return embed


def queue_embed(queue: MusicQueue, current: Track | None, page: int = 1) -> discord.Embed:
    items = list(queue)
    total_pages = max(1, (len(items) + QUEUE_PAGE_SIZE - 1) // QUEUE_PAGE_SIZE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * QUEUE_PAGE_SIZE
    shown = items[start : start + QUEUE_PAGE_SIZE]

    embed = discord.Embed(title="Music Queue", color=discord.Color.green())
    if current:
        embed.add_field(name="Now Playing", value=f"[{current.title}]({current.url})", inline=False)
    if shown:
        lines = [
            f"`{index}.` [{track.title}]({track.url}) - {format_time(track.duration)}"
            for index, track in enumerate(shown, start=start + 1)
        ]
        embed.add_field(name=f"Up Next ({len(items)})", value="\n".join(lines), inline=False)
    else:
        embed.add_field(name="Up Next", value="Queue is empty.", inline=False)
    embed.set_footer(text=f"Page {page}/{total_pages} | Loop: {queue.loop_mode.value}")
    return embed


def resolve_summary_embed(result: ResolveResult) -> discord.Embed:
    if result.is_playlist:
        embed = discord.Embed(title="Playlist Queued", color=discord.Color.green())
        embed.add_field(name="Playlist", value=result.title, inline=False)
        embed.add_field(name="Added", value=str(len(result.tracks)), inline=True)
        embed.add_field(name="Skipped", value=str(result.skipped), inline=True)
    else:
        track = result.tracks[0]
        embed = discord.Embed(title="Queued", description=f"[{track.title}]({track.url})", color=discord.Color.green())
        embed.add_field(name="Source", value=track.source_type, inline=True)
        embed.add_field(name="Duration", value=format_time(track.duration), inline=True)
        if track.thumbnail:
            embed.set_thumbnail(url=track.thumbnail)
    return embed


def message_embed(title: str, description: str, color: discord.Color | None = None) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color or discord.Color.blurple())
