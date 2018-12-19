# Python-Script for migration Pool1-Database into the new Pool2 system
from collections import OrderedDict
import requests
import json
class Migration:
    
    def __init__(self):
        self.auth = {'client_id': 'migration', 'client_secret': 'migration', 'version': '1.1.0'}
        with open('conf/asp.json') as f:
            data = json.load(f)
        self.pillar = data
        # edit the host to internel drops ip
        self.url = [
            "http://localhost:9000/drops/rest/crew/create",
            "http://localhost:9000/drops/rest/user/create",
            "http://localhost:9000/drops/rest/pool1user/create",
            "http://localhost:9000/drops/rest/user/crew"
        ]
    
    def handleCrew(self, crewList):
        finish = len(crewList) / 100
        uuidList = []
        current = 0
        for x in crewList:
            current = current + 1
            print("Insert Crews: ", int(current / finish), "%", end="\r", flush=True)
            headers = { 'Content-Type': 'application/json' }
            r = requests.post(self.url[0], headers=headers, params=self.auth, data=x['model'])
            if r.status_code == 200:
                body = json.loads(r.text)
                x['uuid']['uuid'] = body['id']
            elif r.status_code == 201:
                body = json.loads(r.text)
                x['uuid']['uuid'] = body['id']
            else:
                print("status_code: ", r.status_code, "status_msg: ", r.text, "crew: ", x['model'])
            uuidList.append(x['uuid'])
        print("\n")
        return uuidList
    def ordered(self, d, desired_key_order):
        return OrderedDict([(key, d[key]) for key in desired_key_order])

    def handleUser(self, userList):
        finish = len(userList) / 100
        uuidList = []
        current = 0
        for x in userList:
            current = current + 1
            print("Insert Users: ", int(current / finish), "%", end="\r", flush=True)
            userDict=json.loads(x['model'])
            pool1User = { 
                "email": userDict['email'],
                "confirmed": False
            }
            for p in self.pillar:
                if p['email'] == userDict['email']:
                    x['uuid']['pillar'] = p['pillar']
                    break
                else:
                    continue

            headers = { 'Content-Type': 'application/json' }
            r = requests.post(self.url[1], headers=headers, params=self.auth, data=x['model'])
            if r.status_code == 200:
                body = json.loads(r.text)
                x['uuid']['uuid'] = body['id']
            elif r.status_code == 201:
                body = json.loads(r.text)
                x['uuid']['uuid'] = body['id']
            else:
                print("status_code: ", r.status_code, "status_msg: ", r.text, "user: ", x['model'])
            
            uuidList.append(x['uuid'])
            r = requests.post(self.url[2], headers=headers, params=self.auth, data=json.dumps(pool1User))
            if r.status_code != 200:
                print("status_code: ", r.status_code, "status_msg: ", r.text, "user: ", pool1User)

        print("\n")
        return uuidList

    def handleUserCrew(self, list):
        for x in list:
            if 'pillar' in x:
                url = self.url[3] + "/" + x['user'] + "/" + x['crew'] + "/" + "?" + x['pillar']
                print(url)
                r = requests.post(url, params=self.auth)
                print(r.status_code)
            else: 
                url = self.url[3] + "/" + x['user'] + "/" + x['crew'] + "/"
                print(url)
                r = requests.post(url, params=self.auth)
                print(r.status_code)


