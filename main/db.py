from main.databases.db_abstraction import Nosql
from main.databases.mongo_db import MongoDB

DB_ENGINES = {"MONGODB": MongoDB}

SQL_TYPES = {"NOSQL": Nosql}
