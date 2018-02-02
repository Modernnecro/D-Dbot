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
    def __init__(self):
        """
        It would make more sense to get the class list when you first
        load the cog, and just store and reuse this info. It will make the
        command take half the time!
        """
        # This will be our class field that stores the cache
        # For now, initialise it to an empty dict. It will map
        # lowercase class names to their URLs.
        self.classes = {}

        # Get the data.
        resp = requests.get('http://www.dnd5eapi.co/api/startingequipment')
        # syntax: `assert condition, msg to show if false'
        assert resp.status_code == 200, f'Unexpected response {resp.reason}.'
        data = resp.json()

        # { "count": int, "results": [...] }
        # we want to get the results
        results = data['results']

        # The results should be a list of dicts. Each dict has two keys:
        # "class", which is a string, and "url" which is a string URL.
        # We get the lowercase variant of the class so we can match case
        # insensitive later
        # [{"class": str, "url": url}, {"class": str, "url": url}]
        for pair in results:
            klass = pair['class'].lower()
            url = pair['url']
            self.classes[klass] = url

    @commands.command(aliases=('startingequipment', 'startequipment'))
    async def seq(self, ctx, *, klass=None):
        # First attempt to find the class.
        if klass is None:
            return await ctx.send(
                f'Pick from {", ".join(n for n in self.classes.keys())}')


        try:
            url = self.classes[klass.lower()]
        except KeyError:
            # Handle if the klass given is not in the cache.
            return await ctx.send(
                'That is not a valid class. You can pick from: '
                + ', '.join(self.classes.keys())
            )

        # Get the data for that class.
        resp = requests.get(url)
        assert resp.status_code == 200, f'Unexpected response {resp.reason}.'
        data = resp.json()

        '''
        Data will be the following:
        {
            "_id": int,
            "index": int,
            "starting_equipment": [{...}, {...}, {...}],
            "choices_to_make": int,
            "choice_1": [{...}, {...}, {...}],
            ...
            "choice_n": [{...}, {...}, {...}],
            "url": str,
            "name": str
        }
        We want to get the starting equipment first.
        '''

        # Each dict in the list has the format:
        # {"quantity": int, "item": {"name": str, "url": str}}
        # We are only concerned with the name bit.
        starting_equipment = data['starting_equipment']
        # This will now be a list of name strings.
        starting_equipment = [it['item']['name'] for it in starting_equipment]

        # Get the number of choices to make
        choices_to_make = data['choices_to_make']

        # I am going to generate the keys now just to get it out the way
        # and keep the rest of the logic tidy.
        choice_keys = [f'choice_{i + 1}' for i in range(0, choices_to_make)]

        '''
        Choices have the following structure:
        {
            "from": [
                {
                    "quantity": int,
                    "item": {
                        "name": str,
                        "url": str,
                    }
                },
                ...
            ],
            "type": str,
            "choose": int
        }
        We just want each item's name, and the choose field to tell us how many
        we are allowed to choose.
        '''
        # We will simplify this info to make a list of pairs of:
        #     number, [list of item names]
        options = []

        for choice_key in choice_keys:
            # Each choice key has a list of choice objects            
            for choice in data[choice_key]:
                # Number to choose
                number = choice['choose']
                items = (it['item']['name'] for it in choice['from'])

                # Tuples work exactly the same way as lists. The only difference
                # is that you cannot edit them once you have made them.
                pair = (number, items)
                options.append(pair)


        embed = discord.Embed(
            # Capitalise each word.
            title=klass.title(),
            description=f'You start with {", ".join(starting_equipment)}\n\n'
                        'You have the following options:',
            colour=0x54c571)

        for number, items in options:
            embed.add_field(
                name=f'Pick {number} from',
                # Appends a bullet point onto each one
                # I just have substring'ed the first 1024 characters
                # as that is the character limit, and it saves errors later.
                value='\n'.join(f'• {item}' for item in items)[:1024]
            )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(EquipmentCog())
