
class Environment:
    def __init__(self,states,actions):
        self.states=states
        self.actions=actions

    def getStates(self):
        return self.states

    def getActions(self):
        return self.actions

    def getActionsOfState(self,state):
        return self.actions[state]

    def getReward(self):
        pass

    def isTerminal(self):
        pass

    def transit(self,state,action):
        pass
