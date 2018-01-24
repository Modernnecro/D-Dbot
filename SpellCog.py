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


class SpellCog:
    @commands.command(usage='(spell name)', aliases=('spells', 'magic'))
    async def spell(self, ctx, *, msg=None):
        """
        Shows basic information on Spells.
        """
        data = requests.get('http://www.dnd5eapi.co/api/spells').json()
        results = random.randint(1, data['count'])
        if msg is None:
            # If no message is given, give a random spell. Only the name and description.
            data2 = requests.get('http://www.dnd5eapi.co/api/spells/' + str(results)).json()
            descript = ellipses(win1252_to_utf8('\n\n'.join(data2['desc'])), 2048)
            embed = discord.Embed(
                title='Random Spell: ' + data2['name'],
                description=descript,
                color=0xaa44ff,
                url='http://www.dandwiki.com/wiki/SRD:' + data2['name'].replace(' ', '_')
            )
            await ctx.send(embed=embed)
            return
        spell = find(lambda spell: spell['name'] == msg, data['results'])

        if spell is None:
            # if the spell given doesn't exist in the API, return a text
            await ctx.send('Please use a real spell, one from the Dungeons and Dragons Player Handbook')
        else:
            # if the spell does exist, give the full information, and what it does on higher levels.
            data2 = requests.get(spell['url']).json()

            descript = ellipses(win1252_to_utf8('\n\n'.join(data2['desc'])), 2048)

            embed = discord.Embed(
                title=data2['name'],
                description=descript,
                color=0xaa44ff,
                url='http://www.dandwiki.com/wiki/SRD:' + msg.replace(' ', '_')
            )

            if 'higher_level' in data2:
                embed.add_field(
                    name='Higher Level',
                    value=win1252_to_utf8(' '.join(data2['higher_level']))
                )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SpellCog())
