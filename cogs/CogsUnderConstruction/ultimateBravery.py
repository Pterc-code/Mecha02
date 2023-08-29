# Imports
import discord
from discord.ext import commands

import random


class ultimateBravery(commands.Cog):
    """
    Class to hold all events and commands that would be in command class: test

    === Representation Invariants ===
    None
    """

    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command()
    async def challengeMeMortals(self, ctx):
        await ctx.send(str(ctx.author) + ' is playing: ' + '\n' +
                       self.rollChampion() + '\n' +
                       self.rollMastery() + '\n' +
                       self.rollBuild() + '\n' +
                       self.rollSums())

    def rollChampion(self):
        with open('champions.txt') as file:
            champion = random.choice([line.rstrip() for line in file])
            return champion

    def rollBuild(self):
        shoes = random.choice(['Berserker Greaves]', 'Mobility Boots', 'Boots of Swiftness', 'Ionian Boots of Lucidity', 'Mercury Treads', 'Plates Steelcaps', 'Sorcerers Shoes'])
        with open('legendaryItems.txt') as file:
            legendaryItem = random.sample([line.rstrip() for line in file], 4)
        with open('mythicItems.txt') as file:
            mythicItem = [random.choice([line.rstrip() for line in file])]
        return shoes + ', ' + str(mythicItem + legendaryItem).strip('[').strip(']')

    def rollMastery(self):
        branch = {1: 'Precision', 2: 'Domination', 3: 'Sorcery', 4: 'Resolve', 5: 'Inspiration'}
        pick = random.sample(list(branch), 1)
        mastery = 'I AM BROKEN'
        if pick[0] == 1:
            mastery = random.choice(['Press The Attack', 'Lethal Tempo', 'Fleet Footwork', 'Conqueror'])
        elif pick[0] == 2:
            mastery = random.choice(['Electrocute', 'Predator', 'Dark Harvest', 'Hail of Blades'])
        elif pick[0] == 3:
            mastery = random.choice(['Summon Aery', 'Arcane Comet', 'Phase Rush'])
        elif pick[0] == 4:
            mastery = random.choice(['Grasp Of the Undying', 'After Shock', 'Guardian'])
        elif pick[0] == 5:
            mastery = random.choice(['Glacial Augment', 'Unsealed Spellbook', 'First Strike'])
        return branch[pick[0]] + ': ' + mastery

    def rollSums(self):
        with open('summonerSpells.txt') as file:
            summoners = random.sample([line.rstrip() for line in file], 2)
            return str(summoners).strip('[').strip(']')


async def setup(client):
    await client.add_cog(ultimateBravery(client))
