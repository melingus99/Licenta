from random import randint

class Node:
    def __init__(self,value=None,node_id=None):
        self.value=value
        self.children=[]
        self.id=node_id

    def __str__(self):
        return "node@" + str(self.id)

    def is_terminal(self):
        if len(self.children)==True:
            return True
        return False

    def get_children(self):
        return self.children

    def get_random_child(self):
        if self.is_terminal():
            return None
        return self.children[randint(0,len(self.children)-1)]

    def reward(self):
        return self.value

class Tree:
    def __init__(self,root):
        self.root=root
