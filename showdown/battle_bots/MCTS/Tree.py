from random import randint
from collections import defaultdict
import math
from showdown.engine import StateMutator
from showdown.battle import Battle
from showdown.engine.select_best_move import *
from showdown.battle_bots.helpers import format_decision
from copy import deepcopy
class Node:
    def __init__(self,value=None,node_id=None,mutator=None,parent_move=None):
        self.value=value
        self.children=[]
        self.id=node_id
        self.mutator=mutator
        self.parent_move=parent_move

    def __str__(self):
        return "node@" + str(self.id)

    def is_terminal(self):
        if len(self.children)==0:
            return True
        return False

    def expand_children(self):
        user_options,opponent_options=self.mutator.state.get_all_options()
        for i, user_move in enumerate(user_options[:]):
            for j, opponent_move in enumerate(opponent_options[:]):
                state_instructions = get_all_state_instructions(self.mutator, user_move, opponent_move)
                for instructions in state_instructions:
                    self.mutator.apply(instructions.instructions)
                    score = evaluate(self.mutator.state) * instructions.percentage
                    self.children.append(Node(value=score,mutator=deepcopy(self.mutator),parent_move=user_move))
                    self.mutator.reverse(instructions.instructions)

    def get_children(self):
        return self.children

    def get_random_child(self):
        if self.is_terminal():
            return None
        return self.children[randint(0,len(self.children)-1)]

    def reward(self):
        return self.value

    def add_child(self,node):
        self.children.append(node)

class MCTSTree:
    def __init__(self,root=None,exploration_weight=1.4):
        self.root=root
        self.Q = defaultdict(float)  # total reward of each node
        self.N = defaultdict(float)  # total visit count for each node
        self.children = dict()  # children of each node: key is explored node, value is set of children
        self.exploration_weight = exploration_weight


    def choose_succesor(self):
        "Choose the best successor of node. (Choose a move in the game)"
        if self.root.is_terminal():
            raise RuntimeError(f"choose called on terminal node {self.root}")

        if self.root not in self.children:
            self.root=self.root.get_random_child()
            return self.root

        def score(n):
            if self.N[n] == 0:
                return float("-inf")  # avoid unseen moves
            return self.Q[n] / self.N[n]  # average reward

        self.root=max(self.children[self.root], key=score)
        return self.root

    def run(self, num_rollout):
        "Run on iteration of select -> expand -> simulation(rollout) -> backup"
        path = self.select()
        leaf = path[-1]
        self.expand(leaf)
        reward = 0
        for i in range(num_rollout):
            reward += self.simulate(leaf)
        self.backup(path, reward)

    def select(self):
        "Find an unexplored descendent of `node`"
        path = []
        node=self.root
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                # node is either unexplored or terminal
                return path
            unexplored = self.children[node] - self.children.keys()
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)  # descend a layer deeper

    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expanded:
        # a node is fully expanded if and only if all children are explored
        is_all_children_expanded = all(n in self.children for n in self.children[node])
        if not is_all_children_expanded:
            raise ValueError("Can only select fom fully expanded node")

        log_N_parent = math.log(self.N[node])

        def uct(n):
            "Upper confidence bound for trees"
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
                2*log_N_parent / self.N[n]
            )

        return max(self.children[node], key=uct)


    def expand(self,node):
        "Update the `children` dict with the children of `node`"
        if node in self.children:
            return  # already expanded
        node.expand_children()
        self.children[node] = node.get_children()

    def simulate(self, node):
        "Run a random simulation from node as starting point"
        while True:
            if node.is_terminal():
                return node.reward()
            node = node.get_random_child()

    def backup(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward
