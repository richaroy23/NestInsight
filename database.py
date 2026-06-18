import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Richa@23aug",
        database="nestinsight"
    )
conn = connect_db()
print("Connected")