import traceback

import discord
from discord import app_commands
from discord.ext import commands

from mecha.ui.help import HelpView, help_embed


def resolve_extension(name: str) -> str:
    aliases = {
        "admin": "mecha.cogs.admin",
        "basicFunctions": "mecha.cogs.admin",
        "voice": "mecha.cogs.voice",
        "Praise": "mecha.cogs.praise",
        "praise": "mecha.cogs.praise",
        "LeagueGameStatus": "mecha.cogs.league",
        "league": "mecha.cogs.league",
        "music": "mecha.cogs.music",
        "CogsUnderConstruction.music": "mecha.cogs.music",
    }
    return aliases.get(name, name if "." in name else f"mecha.cogs.{name}")


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error) -> None:
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You're missing a required argument!")
            return

        if isinstance(error, commands.CommandNotFound):
            return

        original = getattr(error, "original", error)
        print(f"Command failed: {ctx.command} invoked by {ctx.author} in {ctx.guild}")
        traceback.print_exception(type(original), original, original.__traceback__)
        await ctx.send(f"Command failed:\n`{type(original).__name__}: {original}`")

    @commands.command()
    async def load(self, ctx, extension: str) -> None:
        extension_name = resolve_extension(extension)
        await self.bot.load_extension(extension_name)
        await ctx.send("Loaded " + extension)

    @commands.command()
    async def unload(self, ctx, extension: str) -> None:
        extension_name = resolve_extension(extension)
        await self.bot.unload_extension(extension_name)
        await ctx.send("Unloaded " + extension)

    @commands.command()
    async def reload(self, ctx, extension: str) -> None:
        extension_name = resolve_extension(extension)
        await self.bot.unload_extension(extension_name)
        await self.bot.load_extension(extension_name)
        await ctx.send("Reloaded " + extension)

    @commands.command()
    async def ping(self, ctx) -> None:
        await ctx.send(f"The ping is {round(self.bot.latency * 1000)}ms")

    @commands.command()
    async def clear(self, ctx, amount: int) -> None:
        await ctx.channel.purge(limit=amount)

    @commands.command(name="help")
    async def help(self, ctx) -> None:
        await ctx.send(embed=help_embed(), view=HelpView())

    @app_commands.command(name="help", description="Show bot help by category.")
    async def slash_help(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(embed=help_embed(), view=HelpView(), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
