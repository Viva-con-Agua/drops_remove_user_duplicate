# stream_migration
Insert the Transactions from the old Pool1 System into Pool2

# use

First you need edit the `conf/config.yml` for the database connection:

```
connection:
    host: 'http://172.2.10.2'
mysql:
    host: 172.2.200.1
    user: drops
    passwd: 
    database: drops

```

Final run:

```
  # pip install -r requirements.txt
  python main.py

```
