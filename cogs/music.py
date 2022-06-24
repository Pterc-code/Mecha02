import random
import asyncio
import discord
from discord.ext import commands
import youtube_dl

from pytube import Playlist


class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.playlist = []

    @commands.command()
    async def play(self, ctx, url):
        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format': "bestaudio"}
        vc = ctx.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2,
                                                              **FFMPEG_OPTIONS)
            vc.play(source)

    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()
        await ctx.send('Paused')

    @commands.command()
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        await ctx.send('Resumed')

    @commands.command()
    async def playlist(self, ctx):
        vc = ctx.voice_client

        self.playlist = list(Playlist(ctx.message.content[10:]))
        for video in self.playlist:
            if not vc.is_playing:
                await self.play(ctx, video)
                self.playlist.pop(0)
            else:
                while vc.is_playing():
                    await asyncio.sleep(0.05)
                await self.play(ctx, self.playlist[0])
                self.playlist.pop(0)

    @commands.command()
    async def skip(self, ctx):
        vc = ctx.voice_client

        if not vc.is_playing:
            await ctx.channel.send('What do you want me to skip? There are no songs playing.')
        else:
            await ctx.channel.send('Skip!')
            await ctx.voice_client.stop()
            self.playlist.pop(0)
            await self.play(ctx, self.playlist[0])

    @commands.command()
    async def queue(self, ctx):
        await ctx.send('Queued.')
        nextInQ = ctx.message.content[7:]
        self.playlist.insert(0, nextInQ)


    @commands.command()
    async def shuffle(self, ctx):
        await ctx.channel.send('Shuffled.')
        self.playlist = random.shuffle(self.playlist)[:]


def setup(client):
    client.add_cog(music(client))
