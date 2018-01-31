import io
import json
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


def print_pretty_json(json_string):
    with io.StringIO(json_string) as fp:
        fp.seek(0)
        obj = json.load(fp)
        pretty_json = json.dump(fp, obj, indent=' ' * 4)
        print(pretty_json)


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
            # pprint.pprint(data2)
            style = data2['class']

            embed = discord.Embed(
                title='Equipment for ' + style['name'],
                url='http://www.dandwiki.com/wiki/5e_SRD:' + msg,
                color=0x6767ff
            )
            if 'starting_equipment' in data2:
                seq = data2['starting_equipment']
                # pprint.pprint(seq)
                string = ''
                for item in seq:
                    quantity = item['quantity']
                    thing = item['item']
                    stuff = thing['name']
                    data3 = requests.get(thing['url']).json()
                    # pprint.pprint(data3)
                    armor = data3['equipment_category']
                    if str(armor) == 'Armor':
                        if quantity == 1:
                            string += str(quantity) + ' ' + stuff + ' Armor, '
                        else:
                            string += str(quantity) + ' Armor' + stuff + 's, '
                    else:
                        if quantity == 1:
                            string += str(quantity) + ' ' + stuff + ', '
                        else:
                            string += str(quantity) + ' ' + stuff + 's, '
                # pprint.pprint(string)
                embed.add_field(
                    name='Starting Equipment',
                    value=string[:-2],
                    inline=False
                )
            raw_choices = []
            # print(f'111 -> {data2!r}')

            # Get the choice key-value pairs out of the dict, ignoring anything
            # else.
            for field in data2.keys():
                if field.startswith('choice_'):
                    raw_choices[field] = data2[field]

            choices = {}
            for choice_list in raw_choices.values():
                # pprint.pprint(choice_list)
                # pprint.pprint(raw_choices.values())
                for i, choice in enumerate(choice_list):
                    # pprint.pprint(i)
                    # pprint.pprint(choice)
                    # Generates a sexy list of options.
                    # pprint.pprint(item['item']['name'])
                    # print(f'126 {i} -> {choice["from"]!r}')
                    options = '\n'.join(['- ' + item['item']['name'] for item in choice['from']])
                    # pprint.pprint(options)

                    number_allowed = choice['choose']
                    # pprint.pprint(number_allowed)
                    string = f'Pick {number_allowed} from:\n{options}'
                    # pprint.pprint(string)

                    # Add that to the choices dict:

                    # { 'Choice 1': 'sexy string', 'Choice 2': 'sexy string'}
                    choices[f'Choice {i + 1}'] = string
                    # print(f'137: {i} -> {string!r}', end='\n\n')
                    # pprint.pprint(choices)
                    # print(repr(choices))

            # Usage
            for choice_title, choice_options in choices.items():
                # pprint.pprint(choices.items())
                # pprint.pprint(choice_title)
                # pprint.pprint(choice_options)
                embed.add_field(name=choice_title, value=choice_options)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(EquipmentCog())
