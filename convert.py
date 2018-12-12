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
    UserModel = {
        'email': '',
        'firstName': '',
        'lastName': '',
        'mobilePhone': '',
        'placeOfResidence': '',
        'birthday': 0,
        'sex': ''
    }
    CrewModel = {
        "name": "",
        "cities": [
        ]
    }
    City = {
        'name': '',
        'country': ''
    }
    
    def __init__(self): 
        self.mydb = mysql.connector.connect(
            host="172.2.111.111",
            user="pool",
            passwd="pool",
            database="pool"
        )
        # required sql strings
        self.mysqlString = [
            "SELECT user_id FROM vca1312_usermeta WHERE meta_key=%s && meta_value=%s",
            "SELECT meta_key, meta_value FROM vca1312_usermeta WHERE user_id=%s && (meta_key='last_name' ||  meta_key='nickname' \
            || meta_key='nation')",
            "SELECT ID FROM vca1312_users",
            "SELECT meta_key, meta_value FROM vca1312_usermeta WHERE user_id=%s && \
            (meta_key='first_name' || meta_key='last_name' || meta_key='mobile' || \
            meta_key='residence' || meta_key='birthday' || meta_key='gender')",
            "SELECT user_email FROM vca1312_users WHERE ID=%s",
            "SELECT name FROM vca1312_vca_asm_geography WHERE ID=%s"
        ]
        

    def crew_id_list(self):
        crewIdList = []
        sqlCursor = self.mydb.cursor()
        sqlAtt = ("vca1312_capabilities", 'a:1:{s:4:"city";b:1;}')
        sqlCursor.execute(self.mysqlString[0], sqlAtt)
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
            sqlcursor.execute(self.mysqlString[1], x)
            crew = copy.deepcopy(self.CrewModel)
            city = copy.copy(self.City)
            country = 0
            for x in sqlcursor:
                if x[0] == 'last_name':
                    city['name'] = x[1]
                elif x[0] == 'nickname':
                    crew['name'] = x[1]
                elif x[0] == 'nation':
                    country = x[1]
            sqlcursor.execute(self.mysqlString[5], (country,))
            for x in sqlcursor:
                city['country'] = x[0]
            crew['cities'].append(self.ordered(city, self.CityOrder))
            crewList.append(json.dumps(self.ordered(crew, self.CrewOrder)))
        print("\n")
        return crewList
    
    def user_id_list(self):
        sqlCursor = self.mydb.cursor()
        userIdList = []
        crewIdList = self.crew_id_list()
        sqlCursor.execute(self.mysqlString[2])
        for x in sqlCursor:
            if x in crewIdList:
                continue
            else:
                userIdList.append(x)
        return userIdList        


    def ordered(self, d, desired_key_order):
        return OrderedDict([(key, d[key]) for key in desired_key_order])

    def userConverter(self):
        sqlCursor = self.mydb.cursor()
        userIdList = self.user_id_list()
        userList = []
        finish = len(userIdList) / 100
        current = 0
        for y in userIdList:
            current = current + 1
            print("Build User Json from Database: ", int(current / finish), "%", end="\r", flush=True)
            sqlCursor.execute(self.mysqlString[3], y)
            user = copy.deepcopy(self.UserModel)
            for x in sqlCursor:
                if x[0] == 'first_name':
                    user['firstName'] = x[1]
                elif x[0] == 'last_name':
                    user['lastName'] = x[1]
                elif x[0] == 'mobile':
                    user['mobilePhone'] = x[1]
                elif x[0] == 'residence':
                    user['placeOfResidence'] = x[1]
                elif x[0] == 'birthday':
                    if x[1] != '':
                        user['birthday'] = int(x[1])
                elif x[0] == 'gender':
                    user['sex'] = x[1]
            sqlCursor.execute(self.mysqlString[4], y)
            for z in sqlCursor:
                user['email'] = z[0]
            result = self.ordered(user, self.UserOrder)
            userList.append(json.dumps(user))
        print("\n")
        return userList







