# -*- coding: iso-8859-1 -*-
import mysql.connector
import json
import copy
from collections import OrderedDict

class Converter:

    # Takings models including taking, deposit and deposit confirmation details

    Model = {
        'taking': '',
        'deposit': '',
        'depositConfirmation': ''
    }

    # Transaction models
    
    Amount = {
        'involvedSupporter': {
            'name': 'Tobias Kästle',
            'uuid': '58c8e525-8d50-41ab-9725-d318891c92db'
        },
        'received': '', # transaction_date * 1000
        'sources': [],
        'author': '58c8e525-8d50-41ab-9725-d318891c92db',
        'comment': 'Migration from Pool1',
        'context': {
            "category": "other",
            "description": "Migration from Pool1" # meta_1
        },
        'created': '', # entry_time * 1000 
        'crew': [],
        'depositUnits': [],
        'details': {
            'partner': {}, # when cash == 0 its field
            "reasonForPayment": "", # name substr(0,3) + " - " meta_1  
            'receipt': 0
        },
        'updated': '' # entry_time * 1000 
    }

    Source = {
        "amount": "",
        "category": "", # when account_type == 'donations' its other else other_ec
        "desc": 1,
        "description": "", # meta_4  
        "norms": "", # # when account_type == 'donations' its DONATION else ECONOMIC
        "typeOfSource": {
            "category": "" # when cash == 0 its "extern", else "cash"
        }
    }

    Partner = {
        # SET "name" = meta_3 # when cash == 0
    }

    Crew = {
        "name": "", # name
        "uuid": "" # handled drops_id
    }

    SourceAmount = {
        "amount": '', # amount / 100
        "currency": "EUR"
    }

    # Deposit models

    Deposit = {
        "amount": [], # DepositAmount
        "created": "", # entry_time * 1000 
        "crew": "", # Crew
        "dateOfDeposit": "", # entry_time * 1000
        "depositUnits": [],
        "full": "", # SourceAmount with 0 EUR,
        "supporter": {
            "name": "Tobias Kästle",
            "uuid": "58c8e525-8d50-41ab-9725-d318891c92db"
        },
        "updated": ""
    }

    DepositAmount = {
        "amount": "", # SourceAmount
        "created": "", # entry_time * 1000
        "takingId": "" # !IMPORTANT FILL FROM THE RESPONSE OF TAKING CREATE AND ADD TAKING ID 
    }

    # Deposit confirmation models

    DepositConfirmation = {
        "date": "", # entry_time * 1000
        "id": "", # !IMPORTANT FILL FROM THE RESPONSE OF DEPOSIT CREATE AND ADD DEPOSIT ID 
        "name": "Tobias Kästle",
        "uuid": "58c8e525-8d50-41ab-9725-d318891c92db"
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

        # account_type == ['donations' || 'econ'] ; meta_1 == {DESCRIPTION} ; receipt_status == [] ; cash == [0 = external | 1 = cash], meta_4 == details of source
        self.transactionMysqlString = [
            "SELECT city_id, amount, account_type, transaction_date, meta_1, meta_3, meta_4, cash, entry_time FROM wp_vca_asm_finances_transactions WHERE transaction_type NOT IN ('expenditure', 'transfer') LIMIT 5",
            "SELECT drops_id, geography_id, name FROM wp_vca_asm_geography_mapping, wp_vca_asm_geography WHERE geography_id = id"
        ]
    
    def transaction_list(self):
        sqlCursor = self.mydb.cursor()
        transactionIdList = []
        sqlCursor.execute(self.transactionMysqlString[0])
        for x in sqlCursor:
            transactionIdList.append(x)
        return transactionIdList

    def crew_data(self):
        crewIdList = {}
        sqlCursor = self.mydb.cursor()
        sqlCursor.execute(self.transactionMysqlString[1])
        for x in sqlCursor:
            crewIdList[x[1]] = { 'drops_id': x[0], 'name': x[2] }
        return crewIdList

    def ordered(self, d, desired_key_order):
        return OrderedDict([(key, d[key]) for key in desired_key_order])

    def transactionConverter(self):
        #testcount = 800

        sqlCursor = self.mydb.cursor()

        crewIdList = self.crew_data()
        print(crewIdList)

        # Get all transactions
        transactionIdList = self.transaction_list()
        transactionList = []
        finish = len(transactionIdList) / 100
        current = 0

        # y >> [0] = city_id, [1] = amount, [2] = account_type, [3] = transaction_date, [4] = meta_1, [5] = meta_3, [6] = meta_4, [7] = cash, [8] = entry_time
        for y in transactionIdList:
            print (y)

            current = current + 1
            model = copy.deepcopy(self.Model)
            amount = copy.deepcopy(self.Amount)
            source = copy.deepcopy(self.Source)
            sourceAmount = copy.deepcopy(self.SourceAmount)
            crew = copy.deepcopy(self.Crew)
            partner = copy.deepcopy(self.Partner)
            deposit = copy.deepcopy(self.Deposit)
            depositAmount = copy.deepcopy(self.DepositAmount)
            depositConfirmation = copy.deepcopy(self.DepositConfirmation)
            print("Build Transaction Json from Database: ", int(current / finish), "%", y, end="\r", flush=True)
            
            # Set crew data
            crew['name'] = crewIdList[y[0]]['name']
            crew['uuid'] = crewIdList[y[0]]['drops_id']

            # Set partner Data WHEN cash is 0
            if y[7] == 0:
                partner['name'] = y[5]

            sourceAmount['amount'] = y[1]

            # Set Source
            source['amount'] = sourceAmount

            if y[2] == 'donations':
                source['category'] = 'other'
                source['norms'] = 'DONATION'
            else:
                source['category'] = 'other_ec'
                source['norms'] = 'ECONOMIC'

            source['description'] = y[6]

            # Set source type depending on cash
            if y[7] == 0:
                source['typeOfSource']['category'] = 'extern'
            else:
                source['typeOfSource']['category'] = 'cash'

            # Set amount
            amount['received'] = int(y[3]) * 1000
            amount['sources'].append(source)

            amount['created'] = int(y[8]) * 1000
            amount['updated'] = int(y[8]) * 1000

            amount['crew'] = crew

            amount['details']['description'] = y[4]

            amount['details']['partner'] = partner
            amount['details']['reasonForPayment'] = crew['name'][:3] + ' ' + y[4]         

            # TODO Set deposit

            deposit['created'] = int(y[8]) * 1000
            deposit['updated'] = int(y[8]) * 1000
            deposit['dateOfDeposit'] = int(y[8]) * 1000

            depositAmount['created'] = int(y[8]) * 1000
            depositAmount['amount'] = sourceAmount

            deposit['amount'].append(depositAmount)

            deposit['crew'] = crew

            sourceAmount['amount'] = 0
            deposit['full'] = sourceAmount

            # TODO Set depositConfirmation

            depositConfirmation['created'] = int(y[8]) * 1000

            # Set model

            model['taking'] = amount
            model['deposit'] = deposit
            model['depositConfirmation'] = depositConfirmation

            transactionList.append(model)
           # if testcount == 0:
            #    break
        print("\n")
        return transactionList





