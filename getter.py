#!/usr/bin/env python3.6
import logging
import random
import asyncio
import pprint

import discord
from discord.ext import commands

import discord.utils as utils
import requests


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


def find(predicate, iterable):
    for element in iterable:
        if predicate(element):
            return element
    # else
    return None


def win1252_to_utf8(string):
    return string.encode('windows-1252').decode('utf-8')


@bot.command(usage='(class name)', aliases=('class', 'style'))
async def classes(ctx, *, msg=None):
    """
    Shows basic info on the classes of Dungeons And Dragons
    """
    data = requests.get('http://www.dnd5eapi.co/api/classes').json()

    if msg is None:
        classes = data['results']
        classes = '\n'.join(sorted('• ' + style['name'] for style in classes))
        embed = discord.Embed(
            title='Usable classes',
            description=classes,
            color=0x6767ff
        )
        await ctx.send(embed=embed)

    classes = find(lambda classes: classes['name'] == msg, data['results'])

    if classes is None:
        if msg is None:
            return
        else:
            await ctx.send('Please use a real class, one from the Dungeons and Dragons Player Handbook')
    else:
        data2 = requests.get(classes['url']).json()
        # pprint.pprint(data2)

        embed = discord.Embed(
            title=data2['name'],
            # description=win1252_to_utf8(''.join(data2['subclasses'])),
            url='http://www.dandwiki.com/wiki/5e_SRD:' + msg,
            color=0x6767ff
        )
        if 'hit_die' in data2:
            embed.add_field(
                name='Hit Die',
                value=data2['hit_die'])
            pass
        if 'proficiencies' in data2:
            proficiencies = data2['proficiencies']
            proficiencies = '\n'.join(sorted('• ' + proficiency['name'] for proficiency in proficiencies))
            embed.add_field(
                name='proficiencies',
                value=proficiencies
            )
            pass
        if 'proficiency_choices' in data2:
            proficiencies = data2['proficiency_choices']
            from_list = proficiencies[0]['from']
            from_list = '\n'.join('• ' + item['name'].replace('Skill: ', '') for item in from_list)
            embed.add_field(
                name='Skill Choices',
                value=from_list
            )
        if 'saving_throws' in data2:
            throw = data2['saving_throws']
            throw = ', '.join(throws['name'].replace('Skill: ', '') for throws in throw)
            embed.add_field(
                name='Skill Choices',
                value=throw
            )
        if 'subclasses' in data2:
            subclasses = data2['subclasses']
            subclasses = '\n'.join(sorted('• ' + subclass['name'] for subclass in subclasses))
            embed.add_field(
                name='Subclasses',
                value=subclasses
            )
        await ctx.send(embed=embed)


@bot.command(usage='(monster name)', aliases=('monsters', 'baddies'))
async def monster(ctx, *, msg=None):
    """
    Shows basic information of Monsters of the Monster Manual.
    """
    if msg is None:
        await ctx.send('Please give the name of a monster.')
    data = requests.get('http://www.dnd5eapi.co/api/monsters').json()

    monsters = find(lambda monsters: monsters['name'] == msg, data['results'])

    if monsters is None:
        await ctx.send('Please use the name of a monster.')
    else:
        data2 = requests.get(monsters['url']).json()

        embed = discord.Embed(
            title=data2['name'],
            url='http://www.dandwiki.com/wiki/5e_SRD:' + msg.replace(' ', '_'),
            color=0xff7777
        )
        if 'hit_points' in data2:
            embed.add_field(
                name='Hit points',
                value=data2['hit_points'])
        if 'armor_class' in data2:
            embed.add_field(
                name='Armor Class',
                value=data2['armor_class']
            )
        if 'challenge_rating' in data2:
            embed.add_field(
                name='Challenge Rating',
                value=data2['challenge_rating']
            )
        if 'special_abilities' in data2:
            abilities = data2['special_abilities']
            abilities = '\n'.join(sorted('• ' + ability['name'] for ability in abilities))
            embed.add_field(
                name='Special Abilities',
                value=abilities,
                inline=False
            )
        if 'actions' in data2:
            actions = data2['actions']
            actions = '\n'.join(sorted('• ' + action['name'] for action in actions))
            embed.add_field(
                name='Actions',
                value=actions
            )
        if 'legendary_actions' in data2:
            actions = data2['legendary_actions']
            actions = '\n'.join(sorted('• ' + action['name'] for action in actions))
            embed.add_field(
                name='Legendary Actions',
                value=actions
            )
        await ctx.send(embed=embed)


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
