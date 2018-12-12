# pool_migration
Insert the Accounts from the old Pool1 System into Pool2

# use

First you need edit the `convert.py` for the database connection:

```
  self.mydb = mysql.connector.connect(
            host="172.2.111.111",
            user="pool",
            passwd="pool",
            database="pool"
        )

```
Next you need to edit the rest url in `migration.py`:

```
        self.url = [
            "http://localhost:9000/drops/rest/crew/create",
            "http://localhost:9000/drops/rest/user/create",
            "http://localhost:9000/drops/rest/pool1user/create"
        ]
```
Final run:

```
  pip install -r requirements.txt
  python main.py

```
