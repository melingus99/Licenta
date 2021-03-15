from showdown.battle import Battle
import math
from showdown.engine.select_best_move import *
import concurrent.futures
from showdown.battle_bots.helpers import format_decision
from showdown.engine import StateMutator
from showdown.battle_bots.RL_agent.Config.config import *
import numpy as np

class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_move(self):
        battles=self.prepare_battles(join_moves_together=True)
        max_move_glob_score=-math.inf
        depth=1
        for battle in battles:
            max_score=-math.inf
            state = battle.create_state()
            mutator = StateMutator(state)
            user_options,opponent_options= battle.get_all_options()

            max_move=self.minimax(depth,mutator,user_options,opponent_options,True)


            if max_move[1]>max_move_glob_score:
                max_move_glob=max_move[0]
                max_move_glob_score=max_move[1]

            # if register_data==True:
            #     user_active=battle.user.active.base_name
            #     opponent_active=battle.opponent.active.base_name
            #     f=open('C:\\Users\\Bubu\\Licenta\\showdown\\battle_bots\\RL_agent\\Config\\training_set.txt','a')
            #     f.write(str(user_active)+str(opponent_active)+','+str(max_move[0])+','+str(max_move[1])+'\n')
            #     f.close()

        return format_decision(self,max_move_glob)


    def minimaxThread(self,depth,mutator,user_move,opponent_options):
        if depth==0:
            min_score=math.inf
            for j, opponent_move in enumerate(opponent_options[:]):
                score=0
                state_instructions = get_all_state_instructions(mutator, user_move, opponent_move)
                for instructions in state_instructions:
                    mutator.apply(instructions.instructions)
                    t_score = evaluate(mutator.state)
                    score += (t_score * instructions.percentage)
                    mutator.reverse(instructions.instructions)
                if score<min_score:
                    min_score=score

            max_score=min_score
            max_move=(user_move,max_score)

        else:
            max_score=-math.inf
            min_score=math.inf
            for j, opponent_move in enumerate(opponent_options[:]):
                state_instructions = get_all_state_instructions(mutator, user_move, opponent_move)
                score=0
                for instructions in state_instructions:
                    mutator.apply(instructions.instructions)
                    next_turn_user_options, next_turn_opponent_options = mutator.state.get_all_options()
                    executor=concurrent.futures.ThreadPoolExecutor(max_workers=9)
                    results=[]
                    for i in range(len(next_turn_user_options)):
                        future=executor.submit(self.minimaxThread,depth-1,mutator,next_turn_user_options[i],opponent_options)
                        results.append(future.result())

                    executor.shutdown(wait=True)
                    max_score=-math.inf
                    for i in results:
                        if i[1]>max_score:
                            move=i
                            max_score=i[1]
                    score += move[1] * instructions.percentage
                    mutator.reverse(instructions.instructions)
                if score<min_score:
                    min_score=score

            max_score=min_score
            max_move=(user_move,max_score)


        return max_move

    def minimax(self,depth,mutator,user_options,opponent_options,prune):

        if depth==0:
            max_score=-math.inf
            for i, user_move in enumerate(user_options[:]):
                skip=False
                min_score=math.inf
                for j, opponent_move in enumerate(opponent_options[:]):
                    if skip:
                        continue
                    score=0
                    state_instructions = get_all_state_instructions(mutator, user_move, opponent_move)
                    for instructions in state_instructions:
                        mutator.apply(instructions.instructions)
                        t_score = evaluate(mutator.state)
                        score += (t_score * instructions.percentage)
                        mutator.reverse(instructions.instructions)
                    if score<min_score:
                        min_score=score
                    if prune and min_score < max_score:
                        skip = True

                        # MOST of the time in pokemon, an opponent's move that causes a prune will cause a prune elsewhere
                        # move this item to the front of the list to prune faster
                        opponent_options = move_item_to_front_of_list(opponent_options, opponent_move)

                if(min_score>max_score):
                    max_score=min_score
                    max_move=(user_move,max_score)

        else:
            max_score=-math.inf
            for i, user_move in enumerate(user_options[:]):
                skip = False
                min_score=math.inf
                for j, opponent_move in enumerate(opponent_options[:]):
                    if skip:
                        continue
                    state_instructions = get_all_state_instructions(mutator, user_move, opponent_move)
                    score=0
                    for instructions in state_instructions:
                        mutator.apply(instructions.instructions)
                        next_turn_user_options, next_turn_opponent_options = mutator.state.get_all_options()
                        move=self.minimax(depth-1,mutator,next_turn_user_options,next_turn_opponent_options,prune)
                        score += move[1] * instructions.percentage
                        mutator.reverse(instructions.instructions)
                    if score<min_score:
                        min_score=score
                    if prune and min_score < max_score:
                        skip = True

                        # MOST of the time in pokemon, an opponent's move that causes a prune will cause a prune elsewhere
                        # move this item to the front of the list to prune faster
                        opponent_options = move_item_to_front_of_list(opponent_options, opponent_move)

                if(min_score>max_score):
                    max_score=min_score
                    max_move=(user_move,max_score)


        return max_move


