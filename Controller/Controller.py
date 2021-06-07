from constants import TEAMS_PATH
import os
class Controller:
    def  __init__(self):
        pass

    def write_file(self,file_name,text):
        file=open(TEAMS_PATH+"/"+file_name,'w')
        file.write(text)
        file.close()

    def write_env(self,text):
        env=open(".env","w")
        env.write(text)
        env.close()

    def read_teams(self):
        file_list=[]
        for file in os.listdir(TEAMS_PATH):
            file_list.append(file)
        return file_list

    def delete(self,team_name):

        os.remove(TEAMS_PATH+"/"+team_name)
