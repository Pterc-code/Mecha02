# Imports
import random
from discord.ext import commands

from random import choice
from cogs.TextToSpeechFiles.TextToSpeech import is_chinese, vocalizeText

# PraiseFiles list for ease of access
praises = []


# Load PraiseFiles
async def loadPraise():
    praises.clear()
    with open("cogs/PraiseFiles/praises.txt", "r") as file:
        for line in file:
            stripped_line = line.strip()
            praises.append(stripped_line.split('||')[0])


class TextToSpeech(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_message(self, ctx):
        """
        Detects if a certain person typed in chat and give them a praise
        """
        if ctx.author.id == 343271388527853579:  # Daniel
            await ctx.channel.send(random.choice(praises))
        elif ctx.author.id == 526991910074581003:  # Bobby
            await ctx.channel.send(random.choice(praises))
        elif ctx.author.id == 264670780317499403:  # Ashley
            await ctx.channel.send(random.choice(praises))

    # Commands
    @commands.command()
    async def praise(self, ctx):
        """
        Randomly praise the given name in the ctx
        """
        voice_client = ctx.voice_client
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("I'm not in a voice channel. Use `!join` first.")
            return

        praise = ctx.message.content[7:] + ' , ' + choice(praises)
        await vocalizeText(ctx, praise, 'en')

    @commands.command()
    async def say(self, ctx):
        """
        Say in the voice channel of the author the given context
        """
        voice_client = ctx.voice_client
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("I'm not in a voice channel. Use `!join` first.")
            return
        text = ctx.message.content[5:]

        if is_chinese(text):
            target_language = 'zh-CN'
        else:
            target_language = 'en'

        await vocalizeText(ctx, text, target_language)

    @commands.command()
    async def add(self, ctx):
        """
        Add a custom praise
        """
        with open('cogs/TextToSpeechFiles/praises.txt', 'a') as f:
            f.write('\n' + ctx.message.content[5:] + '||' + ctx.author.name)
            f.close()
        await ctx.channel.send('Added praise: ' + ctx.message.content[5:])

    @commands.command()
    async def showPraises(self, ctx):
        """
        Print all praises
        """
        with open("cogs/TextToSpeechFiles/praises.txt", "r") as f:
            for praise in f:
                praise = praise.strip().replace('||', ':  ')
                await ctx.channel.send(praise)


async def setup(client):
    await loadPraise()
    await client.add_cog(TextToSpeech(client))
