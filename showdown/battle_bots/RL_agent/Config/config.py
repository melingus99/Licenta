# from data.parse_smogon_stats import get_pokemon_information,get_smogon_stats_file_name
import json
# pokemon_info=get_pokemon_information(get_smogon_stats_file_name("gen7ou"))
# pokemon_info_half={}
# i=0
# for pokemon in pokemon_info:
#     if i==len(pokemon_info)//2:
#         break
#     pokemon_info_half[pokemon]=pokemon_info[pokemon]
#     i+=1
# states=[]
# for pokemon in pokemon_info_half:
#     states.append(pokemon)
# print(len(states))
# actions=[]
# for pokemon in pokemon_info_half:
#     for move in pokemon_info_half[pokemon]['moves']:
#         if move[0] not in actions:
#             actions.append(move[0])
# print(len(actions))
# actions.append('no action')
# for pokemon in states:
#     actions.append("switch "+pokemon)
#
# print(len(actions))
# Q={}
# for i in states:
#     for j in states:
#         Q[str(i)+str(j)]={}
#         for k in actions:
#            Q[str(i)+str(j)][k]=0
#
# with open('Q.json',"w") as Q_file:
#     json.dump(Q,Q_file)


with open('C:\\Users\\Bubu\\Licenta\\showdown\\battle_bots\\RL_agent\\Config\\Q.json','r') as Q_file:
    Q = json.load(Q_file)
Q_file.close()
alpha=0.1
gamma=0.8
epsilon=0.3
register_data=True
