# Imports
import discord
from discord.ext import commands

import random


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
    async def on_command_error(self, ctx, errors):
        # if isinstance(errors, commands.MissingRequiredArgument):
        #     await ctx.send("You're missing a required argument!")
        await ctx.channel.send(errors)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(status=discord.Status.online,
                                          activity=discord.Game("Mecha 01"))
        print("Bot is online.")

    # Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"The ping is {round(self.client.latency * 1000)}ms")

    @commands.command()
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount)

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel.")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)


def setup(client):
    client.add_cog(basicFunctions(client))
