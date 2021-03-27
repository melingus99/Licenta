from showdown.battle import Battle
from showdown.engine.select_best_move import *
from showdown.battle_bots.helpers import format_decision
from showdown.engine import StateMutator
from showdown.battle_bots.MCTS.Tree import *
from showdown.battle_bots.MCTS.config import *
from copy import deepcopy

class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_move(self):
        root_list=self.generate_init_trees()
        best_root=None
        for root in root_list:
            mcts_tree=MCTSTree(root,exploration_weight)
            for _ in range(num_runs):
                mcts_tree.run(num_rollout=num_rollout)
            # we choose the best greedy action based on simulation results
            new_root = mcts_tree.choose_succesor()
            if best_root==None:
                best_root=new_root
            elif new_root.reward()>best_root.reward():
                best_root=new_root
        return format_decision(self,best_root.parent_move)



    def generate_init_trees(self):
        root_list=[]
        battles=self.prepare_battles(join_moves_together=True)
        for battle in battles:
            state = battle.create_state()
            mutator = StateMutator(state)
            root_list.append(Node(value=evaluate(mutator.state),mutator=deepcopy(mutator)))
        return root_list


