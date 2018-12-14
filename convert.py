import mysql.connector
import json
import copy
from collections import OrderedDict

class Converter:
    
    #Ordered json file
    UserOrder = ('email', 'firstName', 'lastName', 'mobilePhone', 'placeOfResidence', 'birthday', 'sex')
    CrewOrder = ('name', 'cities')
    CityOrder = ('name', 'country')
    
    #Models for jsons
    
    Model = {
        'uuid': '',
        'model': ''
    }
    
    UUID = {
        'uuid': '',
        'id': ''
    }

    User = {
        'email': '',
        'firstName': '',
        'lastName': '',
        'mobilePhone': '',
        'placeOfResidence': '',
        'birthday': 0,
        'sex': ''
    }

    Crew = {
        "name": "",
        "cities": [
        ]
    }
    City = {
        'name': '',
        'country': ''
    }

    UserCrew = {
        'user': '',
        'crew': ''
    }

    
    def __init__(self, config): 

        # change access data for pool1 access
        self.config = config
        self.mydb = mysql.connector.connect(
            host=self.config['mysql']['host'],
            user=self.config['mysql']['user'],
            passwd=self.config['mysql']['passwd'],
            database=self.config['mysql']['database']
        )
        # required sql strings
        
        self.crewMysqlString = [
            "SELECT user_id FROM vca1312_usermeta WHERE meta_key=%s && meta_value=%s",
            "SELECT meta_key, meta_value FROM vca1312_usermeta WHERE user_id=%s && (meta_key='last_name' ||  meta_key='nickname' \
            || meta_key='nation' || meta_key='city')",
            "SELECT name, id FROM vca1312_vca_asm_geography WHERE ID=%s"
        ]

        self.userMysqlString = [
            "SELECT ID FROM vca1312_users",
            "SELECT meta_value FROM vca1312_usermeta WHERE user_id=%s && meta_key='first_name'", 
            "SELECT meta_value FROM vca1312_usermeta WHERE user_id=%s && meta_key='last_name'", 
            "SELECT meta_value FROM vca1312_usermeta WHERE user_id=%s && meta_key='mobile'",
            "SELECT meta_value FROM vca1312_usermeta WHERE user_id=%s && meta_key='residence'",
            "SELECT meta_value FROM vca1312_usermeta WHERE user_id=%s && meta_key='birthday'", 
            "SELECT meta_value FROM vca1312_usermeta WHERE user_id=%s && meta_key='gender'", 
            "SELECT meta_value FROM vca1312_usermeta WHERE user_id=%s && meta_key='city'",
            "SELECT user_email FROM vca1312_users WHERE ID=%s"
        ]
        

    def crew_id_list(self):
        crewIdList = []
        sqlCursor = self.mydb.cursor()
        sqlAtt = ("vca1312_capabilities", 'a:1:{s:4:"city";b:1;}')
        sqlCursor.execute(self.crewMysqlString[0], sqlAtt)
        for x in sqlCursor:
            crewIdList.append(x)
        return crewIdList

    def crewConverter(self):
        sqlcursor = self.mydb.cursor()
        crewIdList = self.crew_id_list()
        crewList = []
        finish = len(crewIdList) / 100
        current = 0
        for x in crewIdList:
            current = current + 1
            print("Build Crew Json from Database: ", int(current / finish), "%", end="\r", flush=True)
            sqlcursor.execute(self.crewMysqlString[1], x)
            crew = copy.deepcopy(self.Crew)
            city = copy.deepcopy(self.City)
            uuid = copy.deepcopy(self.UUID)
            model = copy.deepcopy(self.Model)
            country = 0
            id = 0
            for x in sqlcursor:
                if x[0] == 'last_name':
                    city['name'] = x[1]
                elif x[0] == 'nickname':
                    crew['name'] = x[1]
                elif x[0] == 'nation':
                    country = x[1]
                elif x[0] == 'city':
                    id = x[1]
            sqlcursor.execute(self.crewMysqlString[2], (country,))
            uuid['id']=id
            for x in sqlcursor:
                city['country'] = x[0]
            crew['cities'].append(self.ordered(city, self.CityOrder))
            model['uuid'] = uuid
            model['model'] = json.dumps(self.ordered(crew, self.CrewOrder))
            crewList.append(model)

            
        print("\n")
        return crewList
    
    def user_id_list(self):
        sqlCursor = self.mydb.cursor()
        userIdList = []
        crewIdList = self.crew_id_list()
        sqlCursor.execute(self.userMysqlString[0])
        for x in sqlCursor:
            if x in crewIdList:
                continue
            else:
                userIdList.append(x)
        return userIdList        


    def ordered(self, d, desired_key_order):
        return OrderedDict([(key, d[key]) for key in desired_key_order])

    def userConverter(self):
        testcount = 120

        sqlCursor = self.mydb.cursor()
        userIdList = self.user_id_list()
        userList = []
        finish = len(userIdList) / 100
        current = 0
        for y in userIdList:
            testcount = testcount - 1
            current = current + 1
            user = copy.deepcopy(self.User)
            uuid = copy.deepcopy(self.UUID)
            model = copy.deepcopy(self.Model)
            print("Build User Json from Database: ", int(current / finish), "%", y, end="\r", flush=True)
            
            sqlCursor.execute(self.userMysqlString[1], y)
            for x in sqlCursor:
                user['firstName'] = x[0]
            sqlCursor.execute(self.userMysqlString[2], y)
            for x in sqlCursor:
                user['lastName'] = x[0]
            sqlCursor.execute(self.userMysqlString[3], y)
            for x in sqlCursor:
                user['mobilePhone'] = x[0]
            sqlCursor.execute(self.userMysqlString[4], y)
            for x in sqlCursor:
                user['placeOfResidence'] = x[0]
            sqlCursor.execute(self.userMysqlString[5], y)
            for x in sqlCursor:
                if x[0] != '':
                    user['birthday'] = int(x[0])
            sqlCursor.execute(self.userMysqlString[6], y)
            for x in sqlCursor:
                user['sex'] = x[0]
            sqlCursor.execute(self.userMysqlString[7], y)
            for x in sqlCursor:
                id = x[0] 
            sqlCursor.execute(self.userMysqlString[8], y)
            uuid['id']=id
            for z in sqlCursor:
                user['email'] = z[0]
            #result = self.ordered(user, self.UserOrder)
            model['uuid'] = uuid
            model['model'] = json.dumps(user)
            userList.append(model)
            if testcount == 0:
                break
        print("\n")
        return userList

    def buildUserCrewList(self, userList, crewList):
        userCrewList = []
        finish = len(userList) / 100
        current = 0
        for x in userList:
            current = current + 1
            print("Build User Json from Database: ", int(current / finish), "%", end="\r", flush=True)
            crewUser = copy.deepcopy(self.UserCrew)
            if x['id'] != 0:
                for y in crewList:
                    if y['id'] == x['id']:
                        crewUser['user'] = x['uuid']
                        crewUser['crew'] = y['uuid']
                        userCrewList.append(crewUser)
                    else:
                        continue
            else:
                continue
        return userCrewList






