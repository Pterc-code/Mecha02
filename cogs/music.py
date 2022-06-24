import random
import asyncio

import discord
from discord.ext import commands
import youtube_dl

from pytube import Playlist
from pytube import YouTube

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.playlist = []

    @commands.command()
    async def _play(self, ctx, url):
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'}
        YDL_OPTIONS = {'format': "bestaudio"}
        vc = ctx.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2,
                                                              **FFMPEG_OPTIONS)
            vc.play(source)

    async def _playCont(self, ctx):
        vc = ctx.voice_client
        while self.playlist is not []:
            if vc.is_playing():
                await asyncio.sleep(1000000000000000000000000000000000000000000)
            song = self.playlist.pop(0)
            await ctx.send('Now playing: ' + YouTube(song).title + song)
            await self._play(ctx, song)

    @commands.command()
    async def playlist(self, ctx):
        self.playlist = list(Playlist(ctx.message.content[10:]))
        await self._playCont(ctx)

    @commands.command()
    async def skip(self, ctx):
        ctx.voice_client.stop()
        await self._playCont(ctx)
        await ctx.channel.send('Skip!')

    @commands.command()
    async def queue(self, ctx):
        await ctx.send('Queued.')
        nextInQ = ctx.message.content[7:]
        self.playlist.insert(0, nextInQ)

    @commands.command()
    async def shuffle(self, ctx):
        await ctx.send('Shuffled.')
        self.playlist = random.shuffle(self.playlist)[:]


def setup(client):
    client.add_cog(music(client))
