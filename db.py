import os
import mysql.connector.pooling

def create_db_pool():
    pool_config = {
        'pool_name': 'day_trip_pool',
        'pool_size': 10,
        'host': '52.4.229.207',
        'user': os.getenv('SQL_USER'),
        'password': os.getenv('SQL_PASSWORD'),
        'database': 'basic_db',
        'port': 3306,
        'use_pure': True
    }
    return mysql.connector.pooling.MySQLConnectionPool(**pool_config)

mydb_pool = create_db_pool()

# -------------------

# def pool_buildup():
#     pool_config = {
#     'pool_name': 'day_trip_pool',
#     'pool_size': 10,
#     'host': '52.4.229.207',
#     'user': os.getenv('SQL_USER'),
#     'password': os.getenv('SQL_PASSWORD'),
#     'database': 'basic_db',
#     'port':3306,
#     'use_pure': True
# }
#     mydb_pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
#     connection = mydb_pool.get_connection()
#     connection.ssl_disabled = True
#     return connection