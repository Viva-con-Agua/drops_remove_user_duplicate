from convert import Converter
from migration import Migration
#load config file 
def main():
    c = Converter()
    m = Migration()
    crewList = c.crewConverter()
    m.handleCrew(crewList)
    userList = c.userConverter()
    m.handleUser(userList)
    print(config)

if __name__ == "__main__":
    main()
