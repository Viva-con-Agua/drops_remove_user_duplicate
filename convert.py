# -*- coding: utf-8 -*-
import mysql.connector
import json
import copy
import uuid
from collections import OrderedDict

class Converter:

    # User to be deleted including user_id and profile_id

    Model = {
        'user_ids': '',
        'profile_ids': '',
        'supporter_ids': '',
        'token_ids': ''
    }

    CrewData = {
        'min_id': '',
        'supporter_id': '',
        'crew_id': '',
        'role': '',
        'pillar': ''
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

        # 0 email
        # 1 min id
        # 2 id list
        # 3 count
        self.transactionMysqlString = [
            # GET ALL DUPLICATED USERS
            "SELECT email, MIN(id) AS min_id, GROUP_CONCAT(id ORDER BY id) AS id_list, COUNT(*) AS cnt FROM Profile GROUP BY email HAVING cnt > 1 ORDER BY min_id",
            "SELECT GROUP_CONCAT(id) FROM Supporter WHERE profile_id IN (%s)",
            "SELECT GROUP_CONCAT(id) FROM User WHERE id IN (SELECT user_id FROM Profile WHERE Profile.id IN (%s))",
            "SELECT GROUP_CONCAT(OauthToken.id) as id_list FROM OauthToken INNER JOIN User ON HEX(public_id) = HEX(user_id) WHERE User.id IN (%s);",
            "SELECT MIN(id) AS id, supporter_id, crew_id, role, pillar, COUNT(*) AS cnt FROM Supporter_Crew GROUP BY supporter_id, crew_id, role, pillar HAVING cnt > 1"
        ]

        self.deleteMysqlString = [
            "DELETE FROM Supporter_Crew WHERE supporter_id IN(%s)",
            "DELETE FROM Address WHERE supporter_id IN(%s)",
            "DELETE FROM Supporter WHERE id IN(%s)",
            "DELETE FROM LoginInfo WHERE profile_id IN(%s)",
            "DELETE FROM PasswordInfo WHERE profile_id IN(%s)",
            "DELETE FROM Profile WHERE id IN(%s)",
            "DELETE FROM OauthToken WHERE id IN (%s)",
            "DELETE FROM User WHERE id IN(%s);",
            "DELETE FROM Supporter_Crew WHERE supporter_id = %s AND crew_id = %s AND pillar %s AND role %s AND id != %s"
        ]
    
    def transaction_list(self):
        sqlCursor = self.mydb.cursor()
        transactionIdList = []
        sqlCursor.execute(self.transactionMysqlString[0])
        for x in sqlCursor:
            transactionIdList.append(x)
        return transactionIdList

    def supporter_crew_list(self):
        sqlCursor = self.mydb.cursor()
        supporterIdList = []
        sqlCursor.execute(self.transactionMysqlString[4])
        for x in sqlCursor:
            supporterIdList.append(x)
        return supporterIdList

    def ordered(self, d, desired_key_order):
        return OrderedDict([(key, d[key]) for key in desired_key_order])

    def transactionConverter(self):
        #testcount = 800

        sqlCursor = self.mydb.cursor()

        # Get all transactions
        transactionIdList = self.transaction_list()
        transactionList = []
        finish = len(transactionIdList) / 100
        current = 0

        for rawData in transactionIdList:

            current = current + 1
            model = copy.deepcopy(self.Model)
           
            #print("Build List from Database: ", int(current / finish), "%", rawData, end="\r", flush=True)

            email = rawData[0]
            min_id = rawData[1]
            id_list = rawData[2]
            count = rawData[3]

            id_list = id_list.replace(str(min_id) + ",", "")

            model['profile_ids'] = id_list
            # GET Supporter ids

            sqlCursor.execute(self.transactionMysqlString[1]%(id_list))
            for x in sqlCursor:
                model['supporter_ids'] = x[0]


            # GET User ids
            sqlCursor.execute(self.transactionMysqlString[2]%(id_list))
            for x in sqlCursor:
                model['user_ids'] = x[0]

            # GET Token ids
            sqlCursor.execute(self.transactionMysqlString[3]%(model['user_ids']))
            for x in sqlCursor:
                model['token_ids'] = x[0]
            
            print(model)
            transactionList.append(model)
           # if testcount == 0:
            #    break


        print("\n")

        current = 0
        finish = len(transactionList) / 100

        self.mydb.autocommit = False
        sqlCursor = self.mydb.cursor()

        for user in transactionList:

            print("DELETE User FROM Database: ", int(current / finish), "%", user, end="\r", flush=True)
            current = current + 1
            try:
                # delete supporter_crew
                sqlCursor.execute(self.deleteMysqlString[0]%(user['supporter_ids']))

                # delete supporter address
                sqlCursor.execute(self.deleteMysqlString[1]%(user['supporter_ids']))

                # delete supporter
                sqlCursor.execute(self.deleteMysqlString[2]%(user['supporter_ids']))

                # delete login_info
                sqlCursor.execute(self.deleteMysqlString[3]%(user['profile_ids']))

                # delete password_info
                sqlCursor.execute(self.deleteMysqlString[4]%(user['profile_ids']))

                # delete profiles
                sqlCursor.execute(self.deleteMysqlString[5]%(user['profile_ids']))

                if user['token_ids'] != None:
                    # delete oauthtoken if exists
                    sqlCursor.execute(self.deleteMysqlString[6]%(user['token_ids']))

                # delete user
                sqlCursor.execute(self.deleteMysqlString[7]%(user['user_ids']))

                #self.mydb.commit()
                self.mydb.rollback()

            except mysql.connector.Error as error :
                print("Failed to delete record (" + user['profile_ids'] + ") to database rollback: {}".format(error))
                self.mydb.rollback()

                # if testcount == 0:
                #    break

        print("\n")
        
        # TODO Cleanup Supporter_Crew
        supporterIdList = self.supporter_crew_list()
        supporterList = []
        finish = len(supporterIdList) / 100
        current = 0

        for supporterData in supporterIdList:

            current = current + 1
           
            print("DELETE Supporter_Crew FROM Database: ", int(current / finish), "%", supporterData, end="\r", flush=True)

            try:

                min_id = supporterData[0]
                supporter_id = supporterData[1]
                crew_id = supporterData[2]
                role = supporterData[3]
                pillar = supporterData[4]

                role_sql = "IS NULL" 
                if role != None:
                    role_sql = "= '" + role + "'"

                
                pillar_sql = "IS NULL"
                if pillar != None:
                    pillar_sql = "= '" + pillar + "'"

                sqlCursor.execute(self.deleteMysqlString[8]%(supporter_id, crew_id, pillar_sql, role_sql, min_id))

                #self.mydb.commit()
                self.mydb.rollback()

            except mysql.connector.Error as error :
                print("Failed to delete record to database rollback: {}".format(error))
                self.mydb.rollback()

        print("\n")
        return transactionList





