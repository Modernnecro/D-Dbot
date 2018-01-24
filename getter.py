#!/usr/bin/env python3.6
import logging
import random

import discord
import requests
from discord.ext import commands


def ellipses(text: str, max_length: int):
    """
    Takes text as input, and returns it as long as it is less than
    max_length. If it is over this, then ellipses are placed over the last
    three characters and the substring from the start to the boundary is
    returned.

    This makes arbitrarily long text blocks safe to place in messages and
    embeds.
    """
    if len(text) > max_length:
        ellipse = '...'
        return text[0:max_length - len(ellipse)] + ellipse
    else:
        return text


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
bot.load_extension('SpellCog')
bot.load_extension('MonsterCog')
bot.load_extension('ClassesCog')


def find(predicate, iterable):
    for element in iterable:
        if predicate(element):
            return element
    # else
    return None


@bot.listen()
async def on_ready():
    print('Ready to play.')


def win1252_to_utf8(string):
    return string.encode('windows-1252').decode('utf-8')


@bot.command(usage='(game to play here)')
async def game(ctx, *, msg):
    """
    A command that makes the bot "play" a game.
    """
    await bot.change_presence(game=discord.Game(name=msg))
    await ctx.send(f'Now playing {msg}.')


@bot.command()
async def presence(ctx, *, status_str):
    available_statuses = {
        'online': discord.Status.online,
        'dnd': discord.Status.dnd,
        'idle': discord.Status.idle,
        'offline': discord.Status.invisible
    }

    if status_str not in available_statuses:
        await ctx.send(f'Valid statuses are: {", ".join(available_statuses.keys())}')
    else:
        await bot.change_presence(status=available_statuses[status_str])


@bot.command(usage='(condition)', aliases=('status', 'statuses', 'conditions'))
async def condition(ctx, *, msg=None):
    """
    Shows what a certain condition does in Dungeons And Dragons.
    """
    data = requests.get('http://www.dnd5eapi.co/api/conditions').json()

    if msg is None:
        condition = data['results']
        condition = '\n'.join(sorted('• ' + status['name'] for status in condition))
        embed = discord.Embed(
            title='Usable conditions    ',
            description=condition,
            color=0x6767ff
        )
        await ctx.send(embed=embed)

    conditions = find(lambda conditions: conditions['name'] == msg, data['results'])

    if conditions is None:
        if msg is None:
            return
        else:
            await ctx.send('Please use a real class, one from the Dungeons and Dragons Player Handbook')
    else:
        data2 = requests.get(conditions['url']).json()
        descript = data2.get('desc', ['No results'])
        descript = '\n'.join(descript)

        embed = discord.Embed(
            title=data2['name'],
            description=descript,
            url='http://www.dandwiki.com/wiki/' + msg.replace(' ', '_'),
            color=0x999955
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
