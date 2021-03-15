from showdown.battle_bots.RL_agent.Config.config import *
import math

def train():
    with open('C:\\Users\\Bubu\\Licenta\\showdown\\battle_bots\\RL_agent\\Config\\Q.json','r') as Q_file:
        Q = json.load(Q_file)
    Q_file.close()
    f=open("C:\\Users\\Bubu\\Licenta\\showdown\\battle_bots\\RL_agent\\Config\\training_set.txt",'r')
    past_state=None
    for line in f.readlines():
        line=line.split(',')
        if len(line) !=3:
            continue
        state=line[0]
        action=line[1]
        current_state=state
        if action.startswith('switch') and past_state is not None:
            current_state=past_state
        reward=float(line[2][0:-1])
        try:
            maxx=-math.inf
            for i in Q[current_state]:
                if Q[current_state][i]>maxx:
                    maxx=Q[current_state][i]

            Q[current_state][action] =\
                (1-alpha)*Q[current_state][action] +\
                alpha * (reward + gamma * maxx- Q[current_state][action])
        except Exception as e:
            print(current_state+" "+action)
            print(e)
        past_state=state
    with open('C:\\Users\\Bubu\\Licenta\\showdown\\battle_bots\\RL_agent\\Config\\Q.json',"w") as Q_file:
        json.dump(Q,Q_file)
    f.close()
    Q_file.close()
    f=open("C:\\Users\\Bubu\\Licenta\\showdown\\battle_bots\\RL_agent\\Config\\training_set.txt",'w')
    f.write('')
    f.close()
