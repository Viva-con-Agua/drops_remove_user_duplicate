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
    transactionList = c.transactionConverter()
    

if __name__ == "__main__":
    main()
