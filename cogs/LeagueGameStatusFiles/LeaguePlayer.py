import requests


def _update_metadata():
    return requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False).json()


class Player:
    def __init__(self, user_name):
        self.user_name = user_name
        self.player_index = self._get_player_index()
        self.kill_count = 0
        self.death_count = 0
        self.assist_count = 0

    def deathDetected(self) -> bool:
        """
        Returns True when player dies, False when player did not die
        """
        death = self.get_death_count()
        if death > self.death_count:
            self.death_count = death
            return True
        return False

    # Gets player death, kill, assist counts
    def get_death_count(self):
        metadata = _update_metadata()
        return metadata['allPlayers'][self.player_index]['scores']['deaths']

    def get_kill_count(self):
        metadata = _update_metadata()
        return metadata['allPlayers'][self.player_index]['scores']['kills']

    def get_assist_count(self):
        metadata = _update_metadata()
        return metadata['allPlayers'][self.player_index]['scores']['assist']

    # Updates player death, kill, assist counts
    def update_death_count(self):
        self.death_count = self.get_death_count()

    def update_kill_count(self):
        self.kill_count = self.get_kill_count()

    def update_assist_count(self):
        self.assist_count = self.get_assist_count()

    # Helper function to get player index in .json file
    def _get_player_index(self) -> int:
        """
        Returns the player index in the .json file
        """
        metadata = _update_metadata()
        for i in range(len(metadata['allPlayers'])):
            if metadata['allPlayers'][i]['summonerName'] == f'{self.user_name}':
                return i
