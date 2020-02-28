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
            self.config['connection']['host'] + "/backend/stream/takings/create",
            self.config['connection']['host'] + "/backend/stream/deposits/create",
            self.config['connection']['host'] + "/backend/stream/deposits/confirm",
            self.config['connection']['host'] + "/drops/webapp/authenticate",
            self.config['connection']['host'] + "/backend/stream/authenticate/drops?route=/backend/stream/identity&ajax=true",
        ]
    
    def handleTransaction(self, transactionList):

        finish = len(transactionList) / 100
        uuidList = []
        current = 0

        headers = { 'Content-Type': 'application/json' }
        session = requests.session()
        resSession = session.post(self.url[3], headers=headers, data=json.dumps(self.auth), allow_redirects=True)
        print("Result drops authenticate: " + str(resSession.status_code) + ": " + resSession.text)
        #headers.update({'cookies': resSession.headers['Set-Cookie'] })


        resStream = session.get(self.url[4])#, allow_redirects=True)
        print("Result stream identity: ", str(resStream.status_code), ": ", resStream.text)
        #headers = resSession.headers
        #headers.update({'Cookie': resStream.headers['Set-Cookie'] })


        session.headers.update({'Content-Type': 'application/json'})
        session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
        
        for x in transactionList:
            current = current + 1
            print("Insert Transaction: ", int(current / finish), "%", end="\r", flush=True)

            if resStream.status_code != 200:
                print("ERROR: Authentication failed:")
                exit(0)

            # TODO Add taking
            resTaking = session.post(self.url[0], data=json.dumps(x['taking']))

            if resTaking.status_code == 200:
                # TODO Add deposit
                #print(str(resTaking.status_code) + ": " + resTaking.text)
                body = json.loads(resTaking.text)

                uuidList.append(body['data'][0]['id'])

                x['deposit']['amount'][0]['takingId'] = body['data'][0]['id']

                if int(x['taking']['created'] / 1000) < 1577836800:
                    rD = session.post(self.url[1], data=json.dumps(x['deposit']))
                    if rD.status_code == 200:
                        body = json.loads(rD.text)
                        x['depositConfirmation']['id'] = body['data'][0]['publicId']

                        #print(x['depositConfirmation'])
                        rDc = session.post(self.url[2], data=json.dumps(x['depositConfirmation']))
                        if rDc.status_code == 200:
                            body = json.loads(rDc.text)
                            #print(rDc.text)
                        else:
                            print("ERROR CONFIRMING DEPOSIT: ", rDc.status_code, "status_msg: ", rDc.text, "transaction: ", x['depositConfirmation'])

                    else:
                        print("ERROR CREATING DEPOSIT: ", rD.status_code, "status_msg: ", rD.text, "transaction: ", x['deposit'])

            else:
                print("ERROR CREATING TAKING: ", resTaking.status_code, "status_msg: ", resTaking.text, "model: ", x['taking'])
        print("\n")
        return uuidList
    def ordered(self, d, desired_key_order):
        return OrderedDict([(key, d[key]) for key in desired_key_order])
