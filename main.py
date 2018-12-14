import yaml
from convert import Converter
from migration import Migration
#load config file 
def loadConfig():
    with open("conf/config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
    return cfg

def main():
    config = loadConfig()
    c = Converter(config)
    m = Migration()
    crewList = c.crewConverter()
    uuidCrewList = m.handleCrew(crewList)
    print("CrewUUIDList done")
    for x in uuidCrewList:
        print(x)
    userList = c.userConverter()
    uuidUserList = m.handleUser(userList)
    for x in uuidUserList:
        print(x)
    userCrewList = c.buildUserCrewList(uuidUserList, uuidCrewList)
    for x in userCrewList:
        print(x)
    m.handleUserCrew(userCrewList)
    #print(config)
    #print(crewList)

if __name__ == "__main__":
    main()
