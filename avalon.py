from enum import Enum
from random import shuffle
import uuid
import random
from dataclasses import dataclass, field
from discord import Member


class Side(Enum):
    good = 0
    evil = 1


ALIGNMENT = {Side.good: "Good", Side.evil: "Evil"}


@dataclass
class Character:
    name: str
    alignment: Side
    description: str
    pic: str

    def get_alignment(self) -> str:
        return ALIGNMENT[self.alignment]


@dataclass
class Player:
    author: Member
    character: Character = field(default=None)


@dataclass
class Quest:
    player_count: int
    players = []
    required_fails: int


PASS = True
FAIL = False


@dataclass
class CompletedQuest(Quest):
    outcome: bool


MERLIN = Character(name='Merlin', alignment=Side.good,
                   description='Merlin sees the evil characters(except Mordred), but he must remain hidden. If good passes three quests, Assassin gets the chance to pick Merlin at the end. If he does, evil wins.', pic='./loyal_servant.jpg')
PERCIVAL = Character(name='Percival', alignment=Side.good,
                     description='Percival sees Merlin. If Morgana is in play, Percival sees Merlin and Morgana but does not know who is who.', pic='./loyal_servant.jpg')
LOYAL_1 = Character(name='Loyal Servant 1', alignment=Side.good,
                    description='Loyal Servant of Authur. You do not see anyone during the night phase.', pic='./loyal_servant.jpg')
LOYAL_2 = Character(name='Loyal Servant 2', alignment=Side.good,
                    description='Loyal Servant of Authur. You do not see anyone during the night phase.', pic='./loyal_servant.jpg')
LOYAL_3 = Character(name='Loyal Servant 3', alignment=Side.good,
                    description='Loyal Servant of Authur. You do not see anyone during the night phase.', pic='./loyal_servant.jpg')
LOYAL_4 = Character(name='Loyal Servant 4', alignment=Side.good,
                    description='Loyal Servant of Authur. You do not see anyone during the night phase.', pic='./loyal_servant.jpg')
ASSASSIN = Character(name='Assassin', alignment=Side.evil,
                     description='The Assassin sees the other Evil characters during the night phase.\nThe Assassin gets the chance to pick Merlin out of the good characters if Good passes three quests. If he chooses correctly, evil wins.', pic='./loyal_servant.jpg')
MORDRED = Character(name='Mordred', alignment=Side.evil,
                    description='Mordred sees the other Evil characters during the night phase.\nMordred is hidden from Merlin', pic='./loyal_servant.jpg')
MORGANA = Character(name='Morgana', alignment=Side.evil,
                    description='Morgana sees the other Evil characters during the night phase.\nMorgana appears as Merlin to Percival', pic='./loyal_servant.jpg')
OBERON = Character(name='Oberon', alignment=Side.evil,
                   description='Oberon is hidden from the other evil characters. You cannot see them, and they do not see you.', pic='./loyal_servant.jpg')


CHARACTERS = {
    5: [MERLIN, LOYAL_1, LOYAL_2, MORDRED, ASSASSIN],
    6: [MERLIN, LOYAL_1, LOYAL_2, LOYAL_3, MORDRED, ASSASSIN],
    7: [MERLIN, PERCIVAL, LOYAL_1, LOYAL_2, MORDRED, ASSASSIN, MORGANA],
    8: [MERLIN, PERCIVAL, LOYAL_1, LOYAL_2, LOYAL_3, MORDRED, ASSASSIN, MORGANA],
    9: [MERLIN, PERCIVAL, LOYAL_1, LOYAL_2, LOYAL_3, LOYAL_4, MORDRED, ASSASSIN, MORGANA],
    10: [MERLIN, PERCIVAL, LOYAL_1, LOYAL_2, LOYAL_3, LOYAL_4, MORDRED, ASSASSIN, MORGANA, OBERON],
}

QUESTS = {
    5: {0: Quest(player_count=2, required_fails=1), 1: Quest(player_count=3, required_fails=1), 2: Quest(player_count=2, required_fails=1), 3: Quest(player_count=3, required_fails=1), 4: Quest(player_count=3, required_fails=1)},
    6: {0: Quest(player_count=2, required_fails=1), 1: Quest(player_count=3, required_fails=1), 2: Quest(player_count=4, required_fails=1), 3: Quest(player_count=3, required_fails=1), 4: Quest(player_count=4, required_fails=1)},
    7: {0: Quest(player_count=2, required_fails=1), 1: Quest(player_count=3, required_fails=1), 2: Quest(player_count=3, required_fails=1), 3: Quest(player_count=4, required_fails=2), 4: Quest(player_count=4, required_fails=1)},
    8: {0: Quest(player_count=3, required_fails=1), 1: Quest(player_count=4, required_fails=1), 2: Quest(player_count=4, required_fails=1), 3: Quest(player_count=5, required_fails=2), 4: Quest(player_count=5, required_fails=1)},
    9: {0: Quest(player_count=3, required_fails=1), 1: Quest(player_count=4, required_fails=1), 2: Quest(player_count=4, required_fails=1), 3: Quest(player_count=5, required_fails=2), 4: Quest(player_count=5, required_fails=1)},
    10: {0: Quest(player_count=3, required_fails=1), 1: Quest(player_count=4, required_fails=1), 2: Quest(player_count=4, required_fails=1), 3: Quest(player_count=5, required_fails=2), 4: Quest(player_count=5, required_fails=1)}
}


class DuplicatePlayerException(Exception):
    pass


class PlayerCountException(Exception):
    pass


class GameAlreadyStartedException(Exception):
    pass


class Avalon:
    def __init__(self, players=[]):
        self.players = players
        self.id = uuid.uuid4()
        self.characters = []
        self.quests = []
        self.current_quest = 0
        self.current_quest_counter = 0
        globals()
        # self.quests: dict = QUESTS[self.num_players]
        # self.characters: dict = CHARACTERS[self.num_players]

    def add_player(self, author) -> None:
        for player in self.players:
            if author == player.author:
                raise DuplicatePlayerException

        self.players.append(Player(author=author))

    def start(self):
        if 5 > len(self.players) or len(self.players) > 10:
            raise PlayerCountException
        if self.current_quest > 0:
            raise GameAlreadyStartedException
        else:
            self.current_quest = 1
            self.characters = CHARACTERS[len(self.players)].copy()
            random.shuffle(self.players)
            random.shuffle(self.characters)
            self.quests = QUESTS[len(self.players)].copy()
            for i in range(len(self.players)):
                self.players[i].character = self.characters.pop()

    def night_phase(self):
        player_visions = []
        for player in self.players:
            if player.character == MERLIN:
                for other_player in self.players:
                    if other_player.character.alignment == Side.evil and other_player.character != MORDRED:
                        player_visions.append((player, other_player))

            elif player.character == PERCIVAL:
                for other_player in self.players:
                    if other_player.character == MERLIN or other_player.character == MORGANA:
                        player_visions.append((player, other_player))

            elif player.character.alignment == Side.evil:
                for other_player in self.players:
                    if player.character != OBERON and other_player.character != OBERON:
                        if other_player.character.alignment == Side.evil and other_player.character != player.character:
                            player_visions.append((player, other_player))

        return player_visions


if __name__ == '__main__':
    game = Avalon()
    game.add_player('bob')
    game.add_player('joe')
    game.add_player('mike')
    game.add_player('sally')
    game.add_player('john')
    game.add_player('Kevin')
    game.add_player('Casie')
    game.add_player('Jeremiah')
    game.add_player('Scott')
    game.add_player('Jason')
    print(id(game))
    game = Avalon(players=[])
    print(id(game))

    # game.start()
    # for player in game.players:
    #     print(player)
    # for vision in game.night_phase():
    #     print(vision)
    # # print(game.night_phase())

'''
Check in players..
'Ready' is triggered.
Give each player a role.

Start
1. Night Phase
    a. evil wakes up
    b. Merlin wakes up
    c. percival wakes up(if in play)

2. Quest Phase:
    a. random person gets first pick
    b. for each quest, team gets five tries to pick the number of people for that quest, if they cant in five tries, evil wins
    c. vote on pick
    d. if majority, get pass/fail 
        i. if there is certain number of failurs, quest fails
'''
