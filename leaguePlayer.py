import requests


class Player:
    def __init__(self, user_name):
        self.user_name = user_name
        self.player_index = None
        self.kill = None
        self.death = None
        self.assist = None
        self.request = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)

    def update_death_count(self):
        request = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
        death = request.json()['allPlayers'][self.player_index]['scores']['deaths']
        if self.death < death:
            self.death = death
            return True
        return False

    def get_death_count(self):
        death = self.request.json()['allPlayers'][self.player_index]['scores']['deaths']
        self.death = death

    def get_kill_count(self):
        kill = self.request.json()['allPlayers'][self.player_index]['scores']['kills']
        self.kill = kill

    def get_assist_count(self):
        assist = self.request.json()['allPlayers'][self.player_index]['scores']['assist']
        self.assist = assist

    def get_player_index(self):
        for i in range(len(self.request.json()['allPlayers'])):
            if self.request.json()['allPlayers'][i]['summonerName'] == f'{self.user_name}':
                self.player_index = i
