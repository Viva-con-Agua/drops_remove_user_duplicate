#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import yaml
from convert import Converter
from migration import Migration
#load config file 
def loadConfig():
    with open("conf/config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return cfg

def main():
    config = loadConfig()
    c = Converter(config)
    m = Migration()
    transactionList = c.transactionConverter()
    
    print(transactionList)
    #uuidtransactionList = m.handleTransaction(transactionList)
    #print("TransactionUUIDList done")
    #for x in uuidtransactionList:
    #    print(x)

    #print(config)
    #print(crewList)

if __name__ == "__main__":
    main()
