import logging

import discord
from discord import app_commands
from discord.ext import commands

from mecha.music.constants import MAX_VOLUME, MIN_VOLUME
from mecha.music.controls import MusicControls
from mecha.music.embeds import message_embed, queue_embed, resolve_summary_embed, track_embed
from mecha.music.errors import MusicError
from mecha.music.music_manager import MusicManager
from mecha.music.queue import LoopMode
from mecha.music.source_resolver import SourceResolver
from mecha.music.spotify_resolver import SpotifyResolver
from mecha.music.youtube_resolver import YouTubeResolver
from mecha.ui.help import HelpView, help_embed
from mecha.utils.safe_reply import safe_reply

log = logging.getLogger(__name__)


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        youtube = YouTubeResolver(bot.settings.music_max_playlist_size)
        spotify = SpotifyResolver(
            bot.settings.spotify_client_id,
            bot.settings.spotify_client_secret,
            bot.settings.music_max_playlist_size,
        )
        self.manager = MusicManager(bot, SourceResolver(youtube, spotify))
        self._synced = False

    async def cog_unload(self) -> None:
        await self.manager.shutdown()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        if self._synced or not self.bot.settings.sync_app_commands:
            return
        try:
            if self.bot.settings.sync_guild_id:
                guild = discord.Object(id=self.bot.settings.sync_guild_id)
                self.bot.tree.copy_global_to(guild=guild)
                synced = await self.bot.tree.sync(guild=guild)
                print(f"Synced {len(synced)} app commands to guild {self.bot.settings.sync_guild_id}.")
            else:
                synced = await self.bot.tree.sync()
                print(f"Synced {len(synced)} global app commands.")
            self._synced = True
        except discord.HTTPException as error:
            log.warning("Could not sync app commands: %s", error)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after) -> None:
        if self.bot.user is None or member.id != self.bot.user.id or member.guild is None:
            return
        if before.channel is not None and after.channel is None:
            player = self.manager.get_player(member.guild.id)
            if player.current or player.queue:
                log.info("Bot disconnected from voice in guild %s; clearing music player.", member.guild.id)
            await player.shutdown(disconnect=False)

    async def _get_player(self, interaction: discord.Interaction):
        if interaction.guild is None:
            raise MusicError("Music commands only work in a server.")
        return self.manager.get_player(interaction.guild.id)

    async def _require_voice_channel(self, interaction: discord.Interaction) -> discord.VoiceChannel:
        if interaction.guild is None:
            raise MusicError("Music commands only work in a server.")
        if not isinstance(interaction.user, discord.Member) or interaction.user.voice is None:
            raise MusicError("Join a voice channel first.")

        channel = interaction.user.voice.channel
        if not isinstance(channel, discord.VoiceChannel):
            raise MusicError("I can only join server voice channels.")

        bot_member = interaction.guild.me
        permissions = channel.permissions_for(bot_member)
        if not permissions.connect:
            raise MusicError("I do not have permission to connect to your voice channel.")
        if not permissions.speak:
            raise MusicError("I do not have permission to speak in your voice channel.")
        return channel

    async def _require_ctx_voice_channel(self, ctx: commands.Context) -> discord.VoiceChannel:
        if ctx.guild is None:
            raise MusicError("Music commands only work in a server.")
        if not isinstance(ctx.author, discord.Member) or ctx.author.voice is None:
            raise MusicError("Join a voice channel first.")

        channel = ctx.author.voice.channel
        if not isinstance(channel, discord.VoiceChannel):
            raise MusicError("I can only join server voice channels.")

        bot_member = ctx.guild.me
        permissions = channel.permissions_for(bot_member)
        if not permissions.connect:
            raise MusicError("I do not have permission to connect to your voice channel.")
        if not permissions.speak:
            raise MusicError("I do not have permission to speak in your voice channel.")
        return channel

    def _player_from_interaction(self, interaction: discord.Interaction):
        if interaction.guild is None:
            raise MusicError("Music commands only work in a server.")
        return self.manager.get_player(interaction.guild.id)

    @app_commands.command(name="play", description="Play a YouTube link, Spotify link, playlist, or search query.")
    @app_commands.describe(query_or_url="YouTube URL, Spotify URL, playlist URL, or search text")
    async def play(self, interaction: discord.Interaction, query_or_url: str) -> None:
        await interaction.response.defer(thinking=True)
        try:
            await interaction.followup.send(embed=message_embed("Resolving", "Looking up that track..."), ephemeral=True)
            voice_channel = await self._require_voice_channel(interaction)
            player = await self._get_player(interaction)
            result = await self.manager.resolver.resolve(query_or_url, interaction.user)
            await player.enqueue(result, voice_channel, interaction.channel)
            await interaction.followup.send(embed=resolve_summary_embed(result), view=MusicControls(self._player_from_interaction))
        except MusicError as error:
            await interaction.followup.send(embed=message_embed("Music Error", str(error), discord.Color.red()), ephemeral=True)
        except Exception as error:
            log.exception("Unexpected /play failure")
            await interaction.followup.send(
                embed=message_embed("Music Error", f"Something went wrong: {type(error).__name__}", discord.Color.red()),
                ephemeral=True,
            )

    @app_commands.command(name="pause", description="Pause the current track.")
    async def pause(self, interaction: discord.Interaction) -> None:
        await self._player_from_interaction(interaction).pause()
        await safe_reply(interaction, embed=message_embed("Paused", "Playback paused."), ephemeral=True)

    @app_commands.command(name="resume", description="Resume playback.")
    async def resume(self, interaction: discord.Interaction) -> None:
        await self._player_from_interaction(interaction).resume()
        await safe_reply(interaction, embed=message_embed("Resumed", "Playback resumed."), ephemeral=True)

    @app_commands.command(name="skip", description="Skip the current track.")
    async def skip(self, interaction: discord.Interaction) -> None:
        await self._player_from_interaction(interaction).skip()
        await safe_reply(interaction, embed=message_embed("Skipped", "Moving to the next track."), ephemeral=False)

    @app_commands.command(name="stop", description="Stop playback, clear the queue, and disconnect.")
    async def stop(self, interaction: discord.Interaction) -> None:
        await self._player_from_interaction(interaction).stop(disconnect=True)
        await safe_reply(interaction, embed=message_embed("Stopped", "Queue cleared and disconnected."), ephemeral=False)

    @app_commands.command(name="disconnect", description="Disconnect the music player.")
    async def music_disconnect(self, interaction: discord.Interaction) -> None:
        await self._player_from_interaction(interaction).stop(disconnect=True)
        await safe_reply(interaction, embed=message_embed("Disconnected", "Left the voice channel."), ephemeral=False)

    @app_commands.command(name="nowplaying", description="Show the current track.")
    async def nowplaying(self, interaction: discord.Interaction) -> None:
        player = self._player_from_interaction(interaction)
        if player.current is None:
            await safe_reply(interaction, embed=message_embed("Now Playing", "Nothing is playing."), ephemeral=True)
            return
        view = MusicControls(self._player_from_interaction)
        await safe_reply(
            interaction,
            embed=track_embed(
                player.current,
                "Now Playing",
                player.queue.loop_mode,
                len(player.queue),
                player.progress_seconds(),
            ),
            view=view,
            ephemeral=False,
        )

    @app_commands.command(name="queue", description="Show the music queue.")
    @app_commands.describe(page="Queue page number")
    async def show_queue(self, interaction: discord.Interaction, page: int = 1) -> None:
        player = self._player_from_interaction(interaction)
        await safe_reply(interaction, embed=queue_embed(player.queue, player.current, page), ephemeral=True)

    @app_commands.command(name="clearqueue", description="Clear queued tracks without disconnecting.")
    async def clearqueue(self, interaction: discord.Interaction) -> None:
        player = self._player_from_interaction(interaction)
        player.queue.clear()
        await safe_reply(interaction, embed=message_embed("Queue Cleared", "Removed all queued tracks."), ephemeral=False)

    @app_commands.command(name="remove", description="Remove a track from the queue.")
    @app_commands.describe(track_number="Track number shown in /queue")
    async def remove(self, interaction: discord.Interaction, track_number: int) -> None:
        player = self._player_from_interaction(interaction)
        try:
            removed = player.queue.remove(track_number)
        except IndexError:
            await safe_reply(interaction, embed=message_embed("Music Error", "That queue position does not exist.", discord.Color.red()), ephemeral=True)
            return
        await safe_reply(interaction, embed=message_embed("Removed", removed.title), ephemeral=False)

    @app_commands.command(name="move", description="Move a queued track.")
    @app_commands.describe(from_position="Current queue position", to_position="New queue position")
    async def move(self, interaction: discord.Interaction, from_position: int, to_position: int) -> None:
        player = self._player_from_interaction(interaction)
        try:
            moved = player.queue.move(from_position, to_position)
        except IndexError:
            await safe_reply(interaction, embed=message_embed("Music Error", "One of those queue positions does not exist.", discord.Color.red()), ephemeral=True)
            return
        await safe_reply(interaction, embed=message_embed("Moved", f"{moved.title} -> position {to_position}"), ephemeral=False)

    @app_commands.command(name="shuffle", description="Shuffle the queue.")
    async def shuffle(self, interaction: discord.Interaction) -> None:
        self._player_from_interaction(interaction).queue.shuffle()
        await safe_reply(interaction, embed=message_embed("Shuffled", "Queue order randomized."), ephemeral=False)

    @app_commands.command(name="loop", description="Set loop mode.")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="off", value="off"),
            app_commands.Choice(name="song", value="song"),
            app_commands.Choice(name="queue", value="queue"),
        ]
    )
    async def loop(self, interaction: discord.Interaction, mode: app_commands.Choice[str]) -> None:
        player = self._player_from_interaction(interaction)
        player.queue.loop_mode = LoopMode(mode.value)
        await safe_reply(interaction, embed=message_embed("Loop Updated", f"Loop mode is now `{mode.value}`."), ephemeral=False)

    @app_commands.command(name="volume", description="Set playback volume from 0 to 200 percent.")
    @app_commands.describe(value="Volume percent, from 0 to 200")
    async def volume(self, interaction: discord.Interaction, value: int) -> None:
        if value < 0 or value > 200:
            await safe_reply(interaction, embed=message_embed("Music Error", "Volume must be between 0 and 200.", discord.Color.red()), ephemeral=True)
            return
        player = self._player_from_interaction(interaction)
        player.set_volume(max(MIN_VOLUME, min(MAX_VOLUME, value / 100)))
        await safe_reply(interaction, embed=message_embed("Volume", f"Volume set to {value}%."), ephemeral=True)

    @app_commands.command(name="musichelp", description="List music and playlist commands.")
    async def musichelp(self, interaction: discord.Interaction) -> None:
        await safe_reply(interaction, embed=help_embed("playback"), view=HelpView(), ephemeral=True)

    @commands.command(name="play")
    async def prefix_play(self, ctx: commands.Context, *, query_or_url: str) -> None:
        try:
            print(f"Prefix play requested by {ctx.author}: {query_or_url}")
            status = await ctx.send(embed=message_embed("Resolving", "Looking up that track..."))
            voice_channel = await self._require_ctx_voice_channel(ctx)
            player = self.manager.get_player(ctx.guild.id)
            result = await self.manager.resolver.resolve(query_or_url, ctx.author)
            await player.enqueue(result, voice_channel, ctx.channel)
            await status.edit(embed=resolve_summary_embed(result), view=MusicControls(self._player_from_interaction))
        except MusicError as error:
            await ctx.send(embed=message_embed("Music Error", str(error), discord.Color.red()))
        except Exception as error:
            log.exception("Unexpected !play failure")
            await ctx.send(embed=message_embed("Music Error", f"Something went wrong: {type(error).__name__}", discord.Color.red()))

    @commands.command(name="pause")
    async def prefix_pause(self, ctx: commands.Context) -> None:
        await self.manager.get_player(ctx.guild.id).pause()
        await ctx.send(embed=message_embed("Paused", "Playback paused."))

    @commands.command(name="resume")
    async def prefix_resume(self, ctx: commands.Context) -> None:
        await self.manager.get_player(ctx.guild.id).resume()
        await ctx.send(embed=message_embed("Resumed", "Playback resumed."))

    @commands.command(name="skip")
    async def prefix_skip(self, ctx: commands.Context) -> None:
        await self.manager.get_player(ctx.guild.id).skip()
        await ctx.send(embed=message_embed("Skipped", "Moving to the next track."))

    @commands.command(name="stop")
    async def prefix_stop(self, ctx: commands.Context) -> None:
        await self.manager.get_player(ctx.guild.id).stop(disconnect=True)
        await ctx.send(embed=message_embed("Stopped", "Queue cleared and disconnected."))

    @commands.command(name="nowplaying")
    async def prefix_nowplaying(self, ctx: commands.Context) -> None:
        player = self.manager.get_player(ctx.guild.id)
        if player.current is None:
            await ctx.send(embed=message_embed("Now Playing", "Nothing is playing."))
            return
        await ctx.send(
            embed=track_embed(
                player.current,
                "Now Playing",
                player.queue.loop_mode,
                len(player.queue),
                player.progress_seconds(),
            )
        )

    @commands.command(name="queue")
    async def prefix_queue(self, ctx: commands.Context, page: int = 1) -> None:
        player = self.manager.get_player(ctx.guild.id)
        await ctx.send(embed=queue_embed(player.queue, player.current, page))

    @commands.command(name="clearqueue")
    async def prefix_clearqueue(self, ctx: commands.Context) -> None:
        self.manager.get_player(ctx.guild.id).queue.clear()
        await ctx.send(embed=message_embed("Queue Cleared", "Removed all queued tracks."))

    @commands.command(name="remove")
    async def prefix_remove(self, ctx: commands.Context, track_number: int) -> None:
        player = self.manager.get_player(ctx.guild.id)
        try:
            removed = player.queue.remove(track_number)
        except IndexError:
            await ctx.send(embed=message_embed("Music Error", "That queue position does not exist.", discord.Color.red()))
            return
        await ctx.send(embed=message_embed("Removed", removed.title))

    @commands.command(name="move")
    async def prefix_move(self, ctx: commands.Context, from_position: int, to_position: int) -> None:
        player = self.manager.get_player(ctx.guild.id)
        try:
            moved = player.queue.move(from_position, to_position)
        except IndexError:
            await ctx.send(embed=message_embed("Music Error", "One of those queue positions does not exist.", discord.Color.red()))
            return
        await ctx.send(embed=message_embed("Moved", f"{moved.title} -> position {to_position}"))

    @commands.command(name="shuffle")
    async def prefix_shuffle(self, ctx: commands.Context) -> None:
        self.manager.get_player(ctx.guild.id).queue.shuffle()
        await ctx.send(embed=message_embed("Shuffled", "Queue order randomized."))

    @commands.command(name="loop")
    async def prefix_loop(self, ctx: commands.Context, mode: str) -> None:
        try:
            loop_mode = LoopMode(mode.lower())
        except ValueError:
            await ctx.send(embed=message_embed("Music Error", "Loop must be `off`, `song`, or `queue`.", discord.Color.red()))
            return
        player = self.manager.get_player(ctx.guild.id)
        player.queue.loop_mode = loop_mode
        await ctx.send(embed=message_embed("Loop Updated", f"Loop mode is now `{loop_mode.value}`."))

    @commands.command(name="volume")
    async def prefix_volume(self, ctx: commands.Context, value: int) -> None:
        if value < 0 or value > 200:
            await ctx.send(embed=message_embed("Music Error", "Volume must be between 0 and 200.", discord.Color.red()))
            return
        player = self.manager.get_player(ctx.guild.id)
        player.set_volume(max(MIN_VOLUME, min(MAX_VOLUME, value / 100)))
        await ctx.send(embed=message_embed("Volume", f"Volume set to {value}%."))

    @commands.command(name="musichelp", aliases=["musiccommands", "playlisthelp"])
    async def prefix_musichelp(self, ctx: commands.Context) -> None:
        await ctx.send(embed=help_embed("playback"), view=HelpView())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
