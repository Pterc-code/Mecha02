from collections import deque
import discord
from discord import ClientException
from discord.ext import commands
from discord.opus import OpusNotLoaded
from gtts import gTTS
import asyncio
from random import choice

file = open("praises.txt", "r")

praises = []
for line in file:
    stripped_line = line.strip()
    praises.append(stripped_line)


class textToSpeech(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command()
    async def praise(self, ctx):
        vc = ctx.voice_client
        if not vc:
            await ctx.send('Not in voice channel!')

        msgQ = deque([])
        praise = ctx.message.content[7:] + ' , ' + choice(praises)
        if not vc.is_playing:
            await self.speak(ctx, vc, praise, 'en')
        else:
            msgQ.append(praise)
            while vc.is_playing():
                await asyncio.sleep(0.05)
            await self.speak(ctx, vc, msgQ.popleft(), 'en')

    @commands.command()
    async def say(self, ctx):
        vc = ctx.voice_client
        if not vc:
            await ctx.send('Not in voice channel!')

        msgQ = deque([])
        if not vc.is_playing:
            await self.speak(ctx, vc, ctx.message.content[5:], 'en')
        else:
            msgQ.append(ctx.message.content[5:])
            while vc.is_playing():
                await asyncio.sleep(0.05)
            await self.speak(ctx, vc, msgQ.popleft(), 'en')

    @commands.command()
    async def shuo(self, ctx):
        vc = ctx.voice_client
        if not vc:
            await ctx.send('Not in voice channel!')

        msgQ = deque([])
        if not vc.is_playing:
            await self.speak(ctx, vc, ctx.message.content[5:], 'zh-CN')
        else:
            msgQ.append(ctx.message.content[5:])
            while vc.is_playing():
                await asyncio.sleep(0.05)
            await self.speak(ctx, vc, msgQ.popleft(), 'zh-CN')

    @commands.command()
    async def add(self, ctx):
        with open('praises.txt', 'a') as f:
            f.write('\n' + ctx.message.content[5:])
            f.close()
        await ctx.channel.send('Added praise: ' + ctx.message.content[5:])

    @commands.command()
    async def showPraises(self, ctx):
        for praise in praises:
            await ctx.channel.send(praise)

    # Helpers
    async def speak(self, ctx, vc, text, lang):
        msg = gTTS(text=text, lang=lang)
        msg.save('temp.mp3')
        try:
            vc.play(discord.FFmpegPCMAudio('temp.mp3'),
                    after=lambda e: print(f"Finished playing: {msg.text}"))
        except ClientException as e:
            await ctx.send(f"A client exception occured:\n`{e}`")
        except TypeError as e:
            await ctx.send(f"TypeError exception:\n`{e}`")
        except OpusNotLoaded as e:
            await ctx.send(f"OpusNotLoaded exception: \n`{e}`")


def setup(client):
    client.add_cog(textToSpeech(client))
