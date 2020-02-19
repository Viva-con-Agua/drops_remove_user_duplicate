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
            "http://stage.vivaconagua.org/backend/stream/takings/create",
            "http://stage.vivaconagua.org/backend/stream/deposits/create",
            "http://stage.vivaconagua.org/backend/stream/deposits/confirm"
        ]
    
    def handleTransaction(self, transactionList):
        finish = len(transactionList) / 100
        uuidList = []
        current = 0
        for x in transactionList:
            current = current + 1
            print("Insert Transaction: ", int(current / finish), "%", end="\r", flush=True)
            headers = { 'Content-Type': 'application/json' }

            # TODO Add taking
            r = requests.post(self.url[0], headers=headers, params=self.auth, data=json.dumps(x['taking']))
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
                    rD = requests.post(self.url[1], headers=headers, params=self.auth, data=x['deposit'])
                    if rD.status_code == 200:
                        body = json.loads(rD.text)
                        x['depositConfirmation'] = body['id']
                        print(rD.text)

                        rDc = requests.post(self.url[2], headers=headers, params=self.auth, data=x['depositConfirmation'])
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
