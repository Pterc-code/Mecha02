import asyncio
from dataclasses import dataclass

import requests
import urllib3

urllib3.disable_warnings()


@dataclass
class LeaguePlayer:
    user_name: str
    player_index: int
    death_count: int = 0
    kill_count: int = 0
    assist_count: int = 0


class LeagueClient:
    def __init__(self, api_url: str) -> None:
        self.api_url = api_url

    async def get_metadata(self) -> dict:
        return await asyncio.to_thread(self._get_metadata_sync)

    def _get_metadata_sync(self) -> dict:
        return requests.get(self.api_url, verify=False).json()

    async def get_all_friends(self, tracked_players: dict[str, str]) -> list[LeaguePlayer]:
        metadata = await self.get_metadata()
        players: list[LeaguePlayer] = []
        for index, user in enumerate(metadata["allPlayers"]):
            if user["summonerName"] in tracked_players:
                players.append(LeaguePlayer(user["summonerName"], index))
        return players

    async def get_scores(self, player: LeaguePlayer) -> dict:
        metadata = await self.get_metadata()
        return metadata["allPlayers"][player.player_index]["scores"]

    async def death_detected(self, player: LeaguePlayer) -> bool:
        death_count = (await self.get_scores(player))["deaths"]
        if death_count > player.death_count:
            player.death_count = death_count
            return True
        return False
