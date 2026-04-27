from discord.ext import commands

from mecha.music.guild_music_player import GuildMusicPlayer
from mecha.music.source_resolver import SourceResolver


class MusicManager:
    def __init__(self, bot: commands.Bot, resolver: SourceResolver) -> None:
        self.bot = bot
        self.resolver = resolver
        self._players: dict[int, GuildMusicPlayer] = {}

    def get_player(self, guild_id: int) -> GuildMusicPlayer:
        if guild_id not in self._players:
            self._players[guild_id] = GuildMusicPlayer(self.bot, guild_id, self.resolver)
        return self._players[guild_id]

    async def shutdown(self) -> None:
        for player in list(self._players.values()):
            await player.stop(disconnect=True)
