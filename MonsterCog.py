import random
import discord
import requests
from discord.ext import commands


def find(predicate, iterable):
    for element in iterable:
        if predicate(element):
            return element
    # else
    return None


def win1252_to_utf8(string):
    # changes text from Windows-1252 encoding to utf-8 encoding, ignores errors
    return string.encode('windows-1252').decode('utf-8', errors='ignore')


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


class MonsterCog:
    @commands.command(usage='(monster name)', aliases=('monsters', 'baddies'))
    async def monster(self, ctx, *, msg=None):
        """
        Shows basic information of Monsters of the Monster Manual.
        """
        data = requests.get('http://www.dnd5eapi.co/api/monsters').json()
        results = random.randint(1, data['count'])
        if msg is None:
            # If no message is given, give a random spell. Only the name and description.
            data2 = requests.get('http://www.dnd5eapi.co/api/spells/' + str(results)).json()
            descript = descript = ellipses(win1252_to_utf8('\n\n'.join(data2['desc'])), 2048)
            embed = discord.Embed(
                title='Random Monster: ' + data2['name'],
                description='For more information use !monster ' + data2['name'],
                color=0xaa44ff,
                url='http://www.dandwiki.com/wiki/SRD:' + data2['name'].replace(' ', '_')
            )
            await ctx.send(embed=embed)

        monsters = find(lambda monsters: monsters['name'] == msg, data['results'])

        if monsters is None:
            await ctx.send('Please give the name of a monster from the Monster Manual.')
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


def setup(bot):
    bot.add_cog(MonsterCog())
