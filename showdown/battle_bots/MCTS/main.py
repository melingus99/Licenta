from showdown.battle import Battle
from showdown.engine.select_best_move import *
from showdown.battle_bots.helpers import format_decision
from showdown.engine import StateMutator

class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_move(self):
        pass

    def generate_tree(self):

