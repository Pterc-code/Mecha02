# Imports
import discord
from discord.ext import commands


class basicFunctions(commands.Cog):
    """
    Class to hold all events and commands that would be in command class: test

    === Representation Invariants ===
    None
    """
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_command_error(self, ctx, errors) -> None:
        if isinstance(errors, commands.MissingRequiredArgument):
            await ctx.send("You're missing a required argument!")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.client.change_presence(status=discord.Status.online,
                                          activity=discord.Game("Mecha 01"))
        print("Bot is online.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after) -> None:
        if self.client.voice_clients is not None: # Checks if the bot is currently in a voice_client
            if len(self.client.voice_clients) == 1: # Checks if the bot is alone
                voice = discord.utils.get(self.client.voice_clients)
                voice.stop()
                await voice.disconnect()

    # Commands
    @commands.command()
    async def ping(self, ctx) -> None:
        await ctx.send(f"The ping is {round(self.client.latency * 1000)}ms")

    @commands.command()
    async def clear(self, ctx, amount: int) -> None:
        await ctx.channel.purge(limit=amount)

    @commands.command()
    async def join(self, ctx) -> None:
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel.")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def disconnect(self, ctx) -> None:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()


def setup(client):
    client.add_cog(basicFunctions(client))
