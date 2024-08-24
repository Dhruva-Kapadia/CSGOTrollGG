import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'csuser',
    'port': 3306,
    'password': 'cs_sucks',
    'database': 'cstroll'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)