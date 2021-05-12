from showdown.battle import Battle
from showdown.engine.select_best_move import *
from showdown.battle_bots.helpers import format_decision
from showdown.battle_bots.RL_agent.Config.config import *
import random as rand

class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)


    def find_best_move(self):
        battles=self.prepare_battles(join_moves_together=True)
        max_score_glob=-math.inf
        try:
            #exploration
            if rand.random()<=epsilon:
                battle=battles[0]
                user_options,opponent_options= battle.get_all_options()
    
                state=battle.user.active.base_name+battle.opponent.active.base_name
                actions=user_options
    
                choice=actions[rand.randint(0,len(actions)-1)]
                max_score_glob=Q[state][choice]
                max_choice=choice
    
            #greedy
            else:
                for battle in battles:
                    user_options,opponent_options= battle.get_all_options()
                    state=battle.user.active.base_name+battle.opponent.active.base_name
                    max_score=-math.inf
    
                    for action in user_options:
                        if Q[state][action]>max_score:
                            max_score=Q[state][action]
                            choice=action
    
                    if max_score>max_score_glob:
                        max_score_glob=max_score
                        max_choice=choice
        except:
            max_choice=user_options[rand.randint(0,len(user_options)-1)]


        return format_decision(self,max_choice)
