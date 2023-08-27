# Imports
import discord
from discord.ext import commands, tasks


class BasicFunctions(commands.Cog):
    """
    Class to hold all basic events and commands
    """
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_command_error(self, ctx, errors) -> None:
        """
        Gives out an error when command is called without proper arguments
        """
        if isinstance(errors, commands.MissingRequiredArgument):
            await ctx.send("You're missing a required argument!")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Prints in terminal indicating when the bot is online
        """
        await self.client.change_presence(status=discord.Status.online,
                                          activity=discord.Game("Mecha 01"))
        print("Bot is online.")
        self.on_voice_state_update.start()

    @tasks.loop(seconds=5)
    async def on_voice_state_update(self) -> None:
        """
        Automatically disconnects the bot when it is alone in a channel
        """
        for guild in self.client.guilds:
            for voice_channel in guild.voice_channels:
                members = voice_channel.members
                if len(members) == 1 and self.client.user in members:
                    voice = discord.utils.get(self.client.voice_clients)
                    voice.stop()
                    await voice.disconnect()

    # Commands
    @commands.command()
    async def ping(self, ctx) -> None:
        """
        Prints bot latency
        """
        await ctx.send(f"The ping is {round(self.client.latency * 1000)}ms")

    @commands.command()
    async def clear(self, ctx, amount: int) -> None:
        """
        Deletes 'amount' of messages
        """
        await ctx.channel.purge(limit=amount)

    @commands.command()
    async def join(self, ctx) -> None:
        """
        Ensure bot is in user's voice channel or connect/move.
        """
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel.")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def disconnect(self, ctx) -> None:
        """
        Disconnects bot from channel
        """
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()


# Setup cog for client
async def setup(client):
    await client.add_cog(BasicFunctions(client))
