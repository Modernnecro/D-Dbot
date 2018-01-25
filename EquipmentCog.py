import pprint

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


class EquipmentCog:
    @commands.command(usage='(class name)', aliases=('startingeq', 'equipment'))
    async def seq(self, ctx, *, msg=None):
        """
        Shows basic info on the classes of Dungeons And Dragons
        """
        data = requests.get('http://www.dnd5eapi.co/api/startingequipment').json()

        if msg is None:
            startingequipment = data['results']
            startingequipment = '\n'.join(sorted('• ' + seq['class'] for seq in startingequipment))
            embed = discord.Embed(
                title='Use of of these classes as an argument:  ',
                description=startingequipment,
                color=0x6767ff
            )
            await ctx.send(embed=embed)

        startingequipment = find(lambda startingequipment: startingequipment['class'] == msg, data['results'])

        if startingequipment is None:
            if msg is None:
                return
            else:
                await ctx.send('Please use a real class, one from the Dungeons and Dragons Player Handbook')
        else:
            data2 = requests.get(startingequipment['url']).json()
            pprint.pprint(data2)
            style = data2['class']

            embed = discord.Embed(
                title='Equipment for ' + style['name'],
                # description=win1252_to_utf8(''.join(data2['subclasses'])),
                url='http://www.dandwiki.com/wiki/5e_SRD:' + msg,
                color=0x6767ff
            )
        await ctx.send(embed=embed)
    

def setup(bot):
    bot.add_cog(EquipmentCog())
