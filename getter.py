#!/usr/bin/env python3.6
import logging
import random
import asyncio
import pprint

import discord
from discord.ext import commands

import discord.utils as utils
import requests

logging.basicConfig(level='INFO')

class Dungeonbot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self._game = None
        self._status = discord.Status.online
        super().__init__(*args, **kwargs)

    async def change_status(self, **kwargs):
        if 'game' not in kwargs:
            kwargs['game'] = self._game
        else:
            self._game = kwargs['game']

        if 'status' not in kwargs:
            kwargs['status'] = self._status
        else:
            self._status = kwargs['status']

        await super().change_presence(**kwargs)

bot = Dungeonbot(command_prefix='!', owner_id=182905629516496897)

def find(predicate, iterable):
    for element in iterable:
        if predicate(element):
            return element
    # else
    return None

def win1252_to_utf8(string):
    return string.encode('windows-1252').decode('utf-8')

@bot.command(usage='(spell name)')
async def spell(ctx, *, msg = None):
    """
    Shows basic information on Spells.
    """
    if msg is None:
        await ctx.send('Please give the name of a spell.')
        return
    data = requests.get('http://www.dnd5eapi.co/api/spells').json()

    spell = find(lambda spell: spell['name'] == msg, data['results'])

    if spell is None:
        await ctx.send('Please use a real spell, one from the Dungeons and Dragons Player Handbook')
    else:
        data2 = requests.get(spell['url']).json()

        embed = discord.Embed(
            title=data2['name'],
            description=win1252_to_utf8(''.join(data2['desc'])),
            color=0xff0505
        )

        if 'higher_level' in data2:
            embed.add_field(
                name='Higher Level',
                value=win1252_to_utf8(' '.join(data2['higher_level']))
            )
            pass


        await ctx.send(embed=embed)

@bot.command(usage='(class name)')
async def classes(ctx, *, msg = None):
    """
    Shows basic info on the classes of Dungeons And Dragons
    """
    if msg is None:
        await ctx.send('Please give the name of a class.')
    data = requests.get('http://www.dnd5eapi.co/api/classes').json()

    classes = find(lambda classes: classes['name'] == msg, data['results'])

    if classes is None:
        await ctx.send('Please use a real class, one from the Dungeons and Dragons Player Handbook')
    else:
        data2 = requests.get(classes['url']).json()

        embed = discord.Embed(
            title=data2['name'],
            #description=win1252_to_utf8(''.join(data2['subclasses'])),
            color=0xff0505
        )
        await ctx.send(embed=embed)

@bot.command(usage='x y (both are numbers)')
async def d(ctx, sides=6, times=1):
    """
    Makes the bot roll a dice of x sides y times
    """
    a = 0
    results = [str(random.randint(1, sides)) for _ in range(0, times)]
    for ans in results:
        a = a + int(ans)
    await ctx.send(f'{", ".join(results)}\nThe resulting score is: {a}.')


with open('token.txt') as fp:
    token = fp.read().strip()

bot.run(token)