import requests

from mecha.config import load_settings


def _update_metadata():
    return requests.get(load_settings().league_api_url, verify=False).json()


class Player:
    def __init__(self, user_name):
        self.user_name = user_name
        self.player_index = self._get_player_index()
        self.kill_count = 0
        self.death_count = 0
        self.assist_count = 0

    def deathDetected(self) -> bool:
        death = self.get_death_count()
        if death > self.death_count:
            self.death_count = death
            return True
        return False

    def get_death_count(self):
        metadata = _update_metadata()
        return metadata["allPlayers"][self.player_index]["scores"]["deaths"]

    def get_kill_count(self):
        metadata = _update_metadata()
        return metadata["allPlayers"][self.player_index]["scores"]["kills"]

    def get_assist_count(self):
        metadata = _update_metadata()
        return metadata["allPlayers"][self.player_index]["scores"]["assist"]

    def update_death_count(self):
        self.death_count = self.get_death_count()

    def update_kill_count(self):
        self.kill_count = self.get_kill_count()

    def update_assist_count(self):
        self.assist_count = self.get_assist_count()

    def _get_player_index(self) -> int:
        metadata = _update_metadata()
        for index, player in enumerate(metadata["allPlayers"]):
            if player["summonerName"] == self.user_name:
                return index
        raise KeyError(self.user_name)
