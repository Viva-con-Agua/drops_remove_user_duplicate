# Python-Script for migration Pool1-Database into the new Pool2 system

import requests
import json
class Migration:
    
    def __init__(self):
        self.auth = {'client_id': 'migration', 'client_secret': 'migration', 'version': '1.1.0'}

        # change host to the internel drops ip
        self.url = [
            "http://localhost:9000/drops/rest/crew/create",
            "http://localhost:9000/drops/rest/user/create",
            "http://localhost:9000/drops/rest/pool1user/create"
        ]
    
    def handleCrew(self, crewList):
        finish = len(crewList) / 100
        current = 0
        for x in crewList:
            current = current + 1
            print("Insert Crews: ", int(current / finish), "%", end="\r", flush=True)
            headers = { 'Content-Type': 'application/json' }
            r = requests.post(self.url[0], headers=headers, params=self.auth, data=x)
            if r.status_code != 200:
                print("status_code: ", r.status_code, "status_msg: ", r.text, "crew: ", x)
        print("\n")

    def handleUser(self, userList):
        finish = len(userList) / 100
        current = 0
        for x in userList:
            current = current + 1
            print("Insert Users: ", int(current / finish), "%", end="\r", flush=True)
            userDict=json.loads(x)
            pool1User = { 
                "email": userDict['email'],
                "confirmed": False
            }
            headers = { 'Content-Type': 'application/json' }
            r = requests.post(self.url[1], headers=headers, params=self.auth, data=x)
            if r.status_code != 200:
                print("status_code: ", r.status_code, "status_msg: ", r.text, "user: ", x)
            r = requests.post(self.url[2], headers=headers, params=self.auth, data=json.dumps(pool1User))
            if r.status_code != 200:
                print("status_code: ", r.status_code, "status_msg: ", r.text, "user: ", x)

        print("\n")

