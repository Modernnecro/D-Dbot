import discord
import requests
from discord.ext import commands
import pprint

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


class ClassesCog:
    @commands.command(usage='(class name)', aliases=('class', 'style'))
    async def classes(self, ctx, *, msg=None):
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
                pprint.pprint(proficiencies)
                from_list = proficiencies[0]['from']
                # pprint.pprint = from_list
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


def setup(bot):
    bot.add_cog(ClassesCog())
