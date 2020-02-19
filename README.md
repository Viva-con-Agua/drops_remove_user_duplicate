# stream_migration
Insert the Transactions from the old Pool1 System into Pool2

# use

First you need edit the `conf/config.yml` for the database connection:

```
connection:
    stream: 172.2.200.3
mysql:
    host: 172.2.1.10
    user: root
    passwd: root
    database: db175370026 

```
Next you need to edit the rest url in `migration.py`:

```
        self.url = [
            "http://172.2.100.3:9000/backend/stream/takings/create",
            "http://172.2.100.3:9000/backend/stream/deposits/create",
            "http://172.2.100.3:9000/backend/stream/deposits/confirm"
        ]
```
Final run:

```
  pip install -r requirements.txt
  python main.py

```
