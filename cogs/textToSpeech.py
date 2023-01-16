import random
from collections import deque
from discord.ext import commands
import asyncio
from random import choice

from staticFunctions import play_in_vc


file = open("praises.txt", "r")

praises = []
for line in file:
    stripped_line = line.strip()
    praises.append(stripped_line.split('||')[0])

file.close()


class textToSpeech(commands.Cog):
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
        # Detects if the user who gave the command is in a voice channel
        voice_client = ctx.voice_client
        if not voice_client:
            await ctx.send('Not in voice channel!')

        # Queue the praises
        msgQ = deque([])
        praise = ctx.message.content[7:] + ' , ' + choice(praises)
        if not voice_client.is_playing:
            await play_in_vc(ctx, voice_client, praise, 'en')
        else:
            msgQ.append(praise)
            while voice_client.is_playing():
                await asyncio.sleep(0.05)
            await play_in_vc(ctx, voice_client, msgQ.popleft(), 'en')

    @commands.command()
    async def say(self, ctx):
        """
        Say in the voice channel of the author the given context, in English
        """
        voice_client = ctx.voice_client
        if not voice_client:
            await ctx.send('Not in voice channel!')

        msgQ = deque([])
        if not voice_client.is_playing:
            await play_in_vc(ctx, voice_client, ctx.message.content[5:], 'en')
        else:
            msgQ.append(ctx.message.content[5:])
            while voice_client.is_playing():
                await asyncio.sleep(0.05)
            await play_in_vc(ctx, voice_client, msgQ.popleft(), 'en')

    @commands.command()
    async def shuo(self, ctx):
        """
        Say in the voice channel of the author the given context, in Chinese
        """
        vc = ctx.voice_client
        if not vc:
            await ctx.send('Not in voice channel!')

        msgQ = deque([])
        if not vc.is_playing:
            await play_in_vc(ctx, vc, ctx.message.content[5:], 'zh-CN')
        else:
            msgQ.append(ctx.message.content[5:])
            while vc.is_playing():
                await asyncio.sleep(0.05)
            await play_in_vc(ctx, vc, msgQ.popleft(), 'zh-CN')

    @commands.command()
    async def add(self, ctx):
        """
        Add a custom praise
        """
        with open('praises.txt', 'a') as f:
            f.write('\n' + ctx.message.content[5:] + '||' + ctx.author.name)
            f.close()
        await ctx.channel.send('Added praise: ' + ctx.message.content[5:])

    @commands.command()
    async def showPraises(self, ctx):
        """
        Print all praises
        """
        f = open("praises.txt", "r")
        for praise in f:
            praise = praise.strip().replace('||', ':  ')
            await ctx.channel.send(praise)

    # Helpers


def setup(client):
    client.add_cog(textToSpeech(client))
