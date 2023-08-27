# Imports
import random
import os
import re
import asyncio
from collections import deque
from discord.ext import commands

from random import choice
import discord
from gtts import gTTS
from discord import ClientException
from discord.opus import OpusNotLoaded


# Load Praise
file = open("praises.txt", "r")

praises = []
for line in file:
    stripped_line = line.strip()
    praises.append(stripped_line.split('||')[0])

file.close()


# Helper function to vocalize text
async def vocalizeText(ctx, text, language) -> None:
    """
    Play the text in the designated voice_client in the prompted language
    """
    folder_path = "cogs/TextToSpeechFiles"
    os.makedirs(folder_path, exist_ok=True)

    tts = gTTS(text=text, lang=language)

    file_path = os.path.join(folder_path, "tts.mp3")
    tts.save(file_path)
    try:
        ctx.voice_client.play(discord.FFmpegPCMAudio('cogs/TextToSpeechFiles/tts.mp3'))
        print(f"Finished playing: {tts.text}")
    except ClientException as e:
        await ctx.send(f"A client exception occured:\n`{e}`")
    except TypeError as e:
        await ctx.send(f"TypeError exception:\n`{e}`")
    except OpusNotLoaded as e:
        await ctx.send(f"OpusNotLoaded exception: \n`{e}`")


# Helper to determine whether text is in chinese
def is_chinese(text) -> bool:
    """
    If text contains chinese then return TRUE
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    return bool(chinese_pattern.search(text))


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


async def setup(client):
    await client.add_cog(TextToSpeech(client))
