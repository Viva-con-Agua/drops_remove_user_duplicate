# -*- coding: utf-8 -*-
# Python-Script for migration Pool1-Database into the new Pool2 system
from collections import OrderedDict
import requests
import json
class Migration:
    
    def __init__(self, config):
        self.config = config
        self.auth = {'email': self.config['drops']['email'], 'password': self.config['drops']['password'], 'rememberMe': False}

        # edit the host to internel drops ip
        self.url = [
            "http://" + self.config['connection']['stream'] + ":9000/backend/stream/takings/create",
            "http://" + self.config['connection']['stream'] + ":9000/backend/stream/deposits/create",
            "http://" + self.config['connection']['stream'] + ":9000/backend/stream/deposits/confirm",
            "http://" + self.config['connection']['drops'] + ":9000/drops/webapp/authenticate"
        ]
    
    def handleTransaction(self, transactionList):



        finish = len(transactionList) / 100
        uuidList = []
        current = 0
        for x in transactionList:
            current = current + 1
            print("Insert Transaction: ", int(current / finish), "%", end="\r", flush=True)
            headers = { 'Content-Type': 'application/json' }

            s = requests.Session()
            res = s.post(self.url[3], headers=headers, data=json.dumps(self.auth))
            print(res.text)
            exit()

            # TODO Add taking
            print(json.dumps(x['taking']))
            r = requests.post(self.url[0], headers=headers, data=json.dumps(x['taking']))
            print(requests.Response())
            if r.status_code == 200:
                # TODO Add deposit
                print(r.text)
                body = json.loads(r.text)

                uuidList.append(body['id'])

                x['deposit']['amount'][0]['takingId'] = body['id']
                print(r.text)
                print(body['id'])

                if x['deposit'] != "":
                    rD = requests.post(self.url[1], headers=headers, data=x['deposit'])
                    if rD.status_code == 200:
                        body = json.loads(rD.text)
                        x['depositConfirmation'] = body['id']
                        print(rD.text)

                        rDc = requests.post(self.url[2], headers=headers, data=x['depositConfirmation'])
                        if rDc.status_code == 200:
                            body = json.loads(rDc.text)
                            print(rDc.text)
                        else:
                            print("status_code: ", rDc.status_code, "status_msg: ", rDc.text, "transaction: ", x['taking'])

                    else:
                        print("status_code: ", rD.status_code, "status_msg: ", rD.text, "transaction: ", x['taking'])

            else:
                print("status_code: ", r.status_code, "status_msg: ", r.text, "model: ", x['taking'])
        print("\n")
        return uuidList
    def ordered(self, d, desired_key_order):
        return OrderedDict([(key, d[key]) for key in desired_key_order])
