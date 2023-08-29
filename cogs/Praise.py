# Imports
import random
import asyncio
from collections import deque
from discord.ext import commands

from random import choice
from cogs.TextToSpeechFiles.TextToSpeech import is_chinese, vocalizeText

# PraiseFiles list for ease of access
praises = []


# Load PraiseFiles
async def loadPraise():
    file = open("cogs/PraiseFiles/praises.txt", "r")

    for line in file:
        stripped_line = line.strip()
        praises.append(stripped_line.split('||')[0])

    file.close()


class TextToSpeech(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.msgQ = deque([])

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

        # Queue the praises
        praise = ctx.message.content[7:] + ' , ' + choice(praises)
        if not voice_client.is_playing:
            await vocalizeText(ctx, praise, 'en')
        else:
            self.msgQ.append(praise)
            while voice_client.is_playing():
                await asyncio.sleep(0.05)
            await vocalizeText(ctx, self.msgQ.popleft(), 'en')

    @commands.command()
    async def say(self, ctx):
        """
        Say in the voice channel of the author the given context
        """
        voice_client = ctx.voice_client
        text = ctx.message.content[5:]

        if is_chinese(text):
            target_language = 'zh-CN'
        else:
            target_language = 'en'

        if not voice_client.is_playing:
            await vocalizeText(ctx, ctx.message.content[5:], target_language)
        else:
            self.msgQ.append(ctx.message.content[5:])
            while voice_client.is_playing():
                await asyncio.sleep(0.05)
            await vocalizeText(ctx, self.msgQ.popleft(), target_language)

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
        f = open("cogs/TextToSpeechFiles/praises.txt", "r")
        for praise in f:
            praise = praise.strip().replace('||', ':  ')
            await ctx.channel.send(praise)


async def setup(client):
    await loadPraise()
    await client.add_cog(TextToSpeech(client))
