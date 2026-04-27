import asyncio
import traceback
from time import monotonic

import discord
from discord.ext import commands, tasks


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._connected_at: dict[int, float] = {}
        self._alone_checks: dict[int, int] = {}

    def _get_author_voice_channel(self, ctx):
        voice_state = getattr(ctx.author, "voice", None)
        if voice_state is not None and voice_state.channel is not None:
            return voice_state.channel

        guild = getattr(ctx, "guild", None)
        if guild is None:
            return None

        member = guild.get_member(ctx.author.id)
        voice_state = getattr(member, "voice", None)
        if voice_state is not None and voice_state.channel is not None:
            return voice_state.channel

        for voice_channel in guild.voice_channels:
            if any(member.id == ctx.author.id for member in voice_channel.members):
                return voice_channel

        return None

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(self.bot.settings.activity_name),
        )
        print("Bot is online.")
        if self.bot.settings.auto_disconnect_when_alone and not self.disconnect_when_alone.is_running():
            print("Auto-disconnect when alone is enabled.")
            self.disconnect_when_alone.start()
        elif not self.bot.settings.auto_disconnect_when_alone:
            print("Auto-disconnect when alone is disabled.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after) -> None:
        if self.bot.user is None or member.id != self.bot.user.id:
            return

        before_channel = getattr(before, "channel", None)
        after_channel = getattr(after, "channel", None)
        print(f"Bot voice state changed: {before_channel} -> {after_channel}.")

    def cog_unload(self) -> None:
        self.disconnect_when_alone.cancel()

    @tasks.loop(seconds=5)
    async def disconnect_when_alone(self) -> None:
        if not self.bot.settings.auto_disconnect_when_alone:
            return

        for voice_client in list(self.bot.voice_clients):
            channel = getattr(voice_client, "channel", None)
            guild = getattr(voice_client, "guild", None)
            guild_id = getattr(guild, "id", 0)
            if channel is None:
                continue

            connected_at = self._connected_at.get(guild_id, 0)
            if monotonic() - connected_at < self.bot.settings.auto_disconnect_grace_seconds:
                continue

            members = list(channel.members)
            human_members = [member for member in members if not member.bot]
            if human_members:
                self._alone_checks[guild_id] = 0
                continue

            self._alone_checks[guild_id] = self._alone_checks.get(guild_id, 0) + 1
            print(
                "Auto-disconnect alone check "
                f"{self._alone_checks[guild_id]}/{self.bot.settings.auto_disconnect_checks} "
                f"for {channel}: members={[str(member) for member in members]}"
            )

            if self._alone_checks[guild_id] >= self.bot.settings.auto_disconnect_checks:
                print(f"Disconnecting from {channel}: no non-bot members detected.")
                voice_client.stop()
                await voice_client.disconnect()
                self._connected_at.pop(guild_id, None)
                self._alone_checks.pop(guild_id, None)

    @commands.command()
    async def join(self, ctx) -> None:
        print(f"Join requested by {ctx.author} ({ctx.author.id}) in guild {ctx.guild}.")
        voice_channel = self._get_author_voice_channel(ctx)
        if voice_channel is None:
            print(f"Join failed: no voice channel found for user {ctx.author} ({ctx.author.id}).")
            await ctx.send(
                "I can't see you in a voice channel. Make sure you're in a server voice channel "
                "I can view, and that the bot has Voice States intent enabled."
            )
            return

        try:
            if ctx.voice_client is None:
                print(f"Connecting to voice channel: {voice_channel} ({voice_channel.id}).")
                voice_client = await voice_channel.connect(timeout=15, reconnect=False)
            else:
                print(f"Moving to voice channel: {voice_channel} ({voice_channel.id}).")
                await ctx.voice_client.move_to(voice_channel)
                voice_client = ctx.voice_client
            self._connected_at[voice_client.guild.id] = monotonic()
            self._alone_checks[voice_client.guild.id] = 0
            await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
            await asyncio.sleep(2)
            print(
                "Post-join voice check: "
                f"is_connected={voice_client.is_connected()}, "
                f"channel={getattr(voice_client, 'channel', None)}, "
                f"tracked_clients={len(self.bot.voice_clients)}"
            )
        except discord.Forbidden:
            print(f"Join failed: missing permission to connect to {voice_channel}.")
            await ctx.send("I don't have permission to connect to that voice channel.")
        except discord.ClientException as error:
            print(f"Join failed: {error}")
            await ctx.send(f"I couldn't join the voice channel:\n`{error}`")
        except discord.ConnectionClosed as error:
            print(f"Join failed: voice websocket closed with {error.code}.")
            if error.code == 4017:
                await ctx.send(
                    "I couldn't join because this voice channel requires Discord's E2EE/DAVE voice protocol. "
                    "Bots using discord.py cannot join that kind of voice channel. Disable E2EE for the channel "
                    "or try a normal voice channel."
                )
            else:
                await ctx.send(f"I couldn't join the voice channel:\n`WebSocket closed with {error.code}`")
        except TimeoutError:
            print(f"Join failed: timed out connecting to {voice_channel}.")
            await ctx.send("I timed out while trying to connect to that voice channel.")
        except Exception as error:
            print(f"Join failed unexpectedly while connecting to {voice_channel}.")
            traceback.print_exception(type(error), error, error.__traceback__)
            await ctx.send(f"I couldn't join the voice channel:\n`{type(error).__name__}: {error}`")

    @commands.command()
    async def disconnect(self, ctx) -> None:
        if ctx.voice_client is not None:
            self._connected_at.pop(ctx.voice_client.guild.id, None)
            self._alone_checks.pop(ctx.voice_client.guild.id, None)
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Voice(bot))
