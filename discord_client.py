import discord
import logging
from avalon import Avalon, DuplicatePlayerException, PlayerCountException, GameAlreadyStartedException
import re
import os

class MockMember:
    def __init__(self, name):
        self.name = name

    async def send(self, string: str):
        print(string)


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        self.avalon = None

    async def on_message(self, message):

        # The bot should ignore private messages
        if message.channel.type == discord.enums.ChannelType.private:
            return

        # the bot should ignore any of it's own messages
        if message.author == self.user:
            return

        match = re.match('-([A-Za-z])+', message.content)

        if match:
            try:
                command = getattr(self, '_'+match.group()[1:]+'_command')
                await command(message)
            except AttributeError as e:
                print(f'{message.content} not found')

    async def _init_command(self, message):
        '''-init  Initialize a new game'''
        if self.avalon:
            await message.channel.send(f'Game already started.')
        else:
            self.avalon = Avalon(players=[])
            self.avalon.add_player(MockMember(name='Bob'))
            self.avalon.add_player(MockMember(name='joe'))
            self.avalon.add_player(MockMember(name='Mike'))
            self.avalon.add_player(MockMember(name='Sally'))
            await message.channel.send(f'Started game {self.avalon.id}')

    async def _join_command(self, message):
        '''-join  Join a game before it starts'''
        if self.avalon is None:
            await message.channel.send('No active game to join!')
        elif len(self.avalon.players) == 10:
            await message.channel.send('Sorry! the max number of players for Avalon is 10')
        else:
            try:
                self.avalon.add_player(message.author)
                await message.channel.send(f'Player {message.author} added')
                await message.author.send(f'You joined game {self.avalon.id}!')
            except DuplicatePlayerException as e:
                await message.channel.send(f'Player {message.author} already added!')

    async def _start_command(self, message):
        '''-start  Start a game'''
        if not self.avalon:
            await message.channel.send('No active game!')

        try:
            self.avalon.start()
        except PlayerCountException:
            await message.channel.send(f'Not enough players!')
            return

        for player in self.avalon.players:
            await player.author.send(f'\nYou are {player.character.name}. You are on the {player.character.get_alignment()} team.\n{player.character.description}\n')

        await message.channel.send(f'Night is about to start, Here are the characters for this game: {[player.character.name for player in self.avalon.players]}')

        for vision in self.avalon.night_phase():
            player = vision[0]
            other_player = vision[1]
            await player.author.send(f'You saw {other_player.author.name} during the night phase')
            print(
                f'{player.author.name} ({player.character.name}) saw {other_player.author.name} ({other_player.character.name})')

        await message.channel.send(f'Night phase complete! Check your DM\'s for details!')

    async def _players_command(self, message):
        '''-players  Get a list of players in the active game'''
        if not self.avalon:
            await message.channel.send('No active game!')
            return

        await message.channel.send(f'Active Players for game id: {self.avalon.id}: {[player.author.name for player in self.avalon.players]}')

    async def _reset_command(self, message):
        '''-reset  Clear the active game'''
        self.avalon = None

    async def _help_command(self, message):
        '''-help  Display the help menu'''
        help_message='Available commands:\n'
        for method in dir(self):
            if method[-8:] == '_command':
                help_message+=getattr(self, method).__doc__+'\n'
        await message.channel.send(help_message)


        


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    client = MyClient()
    client.run(
        os.environ['DISCORD_TOKEN'])


# channel = message.channel
# logging.info(f' Recieved: "{message.content}" responding with: "{message.content}"')
# print(message.author)
# print(dir(message.author))
# await channel.send(message.content)

