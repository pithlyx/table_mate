import sqlite3
import time


def connect_to_database():
    db = input("Enter a database name: ")
    while True:
        try:
            return sqlite3.connect(f"../db/{db}.db")
        except sqlite3.OperationalError:
            print("Waiting for the database to be created...")
            time.sleep(1)


def get_table_keys():
    has_primary_key = False
    keys = []
    types = ["NULL", "INTEGER", "REAL", "TEXT",
             "BLOB", "NUMERIC", "INTEGER PRIMARY KEY"]
    while True:
        key = input("Enter a new key: ").lower()
        if key == "":
            break
        # Check if the key already exists in the list
        elif key not in [k[0] for k in keys]:
            while True:
                key_type = input("Enter a type: ").upper()
                if key_type == "?":
                    print(f"Types: {', '.join(types)}")
                elif key_type in types and (key_type != "INTEGER PRIMARY KEY" or not has_primary_key):
                    keys.append([key, key_type])
                    if key_type == "INTEGER PRIMARY KEY":
                        has_primary_key = True
                    break
                else:
                    print("Invalid type")
        else:
            print("Key already exists")
    return keys


def get_table_name(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]

    while True:
        new_table_name = input("Enter a table name: ")
        if new_table_name not in tables:
            return new_table_name
        print("Table already exists")


def create_table(conn, table_name, table_keys):
    for i, key in enumerate(table_keys):
        table_keys[i] = " ".join(key)
    table_keys = ", ".join(table_keys)
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE {table_name} ({table_keys})")


def show_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    if tables := [table[0] for table in cursor.fetchall()]:
        print(f"Tables: {', '.join(tables)}")


def drop_table(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE {table_name}")


def drop_column(conn, table_name, column_name):
    cursor = conn.cursor()
    cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")


def add_column(conn, table_name, column_name, column_type):
    cursor = conn.cursor()
    cursor.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def main():
    conn = connect_to_database()
    while True:
        show_tables(conn)
        table_name = get_table_name(conn)
        table_keys = get_table_keys()
        print(f"Table: [{table_name}]\nKeys: {table_keys}?")
        option = input("Create table? (y/n): ").lower()
        if option == "y":
            create_table(conn, table_name, table_keys)
        else:
            break
    conn.close()


main()
