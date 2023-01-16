# Imports
import os

from discord.ext import commands
import discord


# sets the command prefix to !
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())


# Basic Commands
@client.command()
async def load(ctx, extension) -> None:
    """
    Loads the cog with name: extension
    """
    client.load_extension(f"cogs.{extension}")


@client.command()
async def unload(ctx, extension) -> None:
    """
    Unloads the cog with name: extension
    """
    client.unload_extension(f"cogs.{extension}")


@client.command()
async def reload(ctx, extension) -> None:
    """
    Reloads the cogs for ease of access
    """
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
    await ctx.send('Reloaded ' + extension)


# Load Cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run("")
