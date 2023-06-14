import json
import math
import os
import sqlite3

CLEAR = False
CLEAR = True
MENU_WIDTH = 100


DB_PATH = "./db"


class Attribute:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'"{self.name}": "{self.value}"'


class Table:
    def __init__(self, name):
        self.name = name
        self.attributes = {}

    def add_attribute(self, attr):
        attributes = attr.lower().split()
        attr_dict = {
            "attr_type_dict": {
                "NULL": ["null"],
                "INTEGER": ["int", "integer"],
                "REAL": ["real"],
                "TEXT": ["text", "txt"],
                "BLOB": ["blob"]
            },
            "type_modifier_dict": {
                "PRIMARY KEY": ["pk"],
                "FOREIGN KEY": ["fk"],
                "REFERENCES": ["ref"],
                "ON DELETE": ["od"],
                "ON UPDATE": ["ou"],
                "AUTOINCREMENT": ["ai"],
                "COLLATE": ["co"],
                "CHECK": ["ch"],
                "NOT NULL": ["nn"],
                "UNIQUE": ["u"],
                "DEFAULT": ["d"]
            }
        }

        if len(attributes) < 2:
            raise ValueError("Valid attributes must have a name and type.")

        attr_name = attributes[0]
        attr_type = attributes[1]

        for attr_value, attr_list in attr_dict["attr_type_dict"].items():
            if attr_type in attr_list:
                attr_type = attr_value
                break
        else:
            raise ValueError(f"Invalid type '{attr_type}'.")

        if len(attributes) > 2:
            type_modifier = attributes[2]
            for attr, attr_aliases in attr_dict["type_modifier_dict"].items():
                if type_modifier in attr_aliases:
                    type_modifier = attr
                    break
            else:
                raise ValueError(f"Invalid type_modifier '{type_modifier}'.")
            attr_type += f" {type_modifier}"

        if attr_name in self.attributes:
            raise ValueError(f"Attribute '{attr_name}' already exists.")
        self.attributes[attr_name] = Attribute(
            attr_name.lower(), attr_type.upper())

    def remove_attribute(self, name):
        if name not in self.attributes:
            raise ValueError
        del self.attributes[name]

    def __repr__(self):
        attributes_str = ', '.join([str(attr)
                                   for attr in self.attributes.values()])
        return f'{{ {attributes_str} }}'

    def print_json(self):
        print(json.dumps({self.name: json.loads(str(self))}, indent=2))


class Database:
    def __init__(self, name, conn):
        self.name = name
        self.tables = {}
        self.load_existing_tables(conn)

    def load_existing_tables(self, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table_name in tables:
            table_name = table_name[0]  # fetchall() returns a list of tuples
            self.tables[table_name] = Table(table_name)
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for column in columns:
                column_name = column[1]
                column_type = column[2]
                self.tables[table_name].attributes[column_name] = Attribute(
                    column_name, column_type)

    def add_table(self, name):
        if name in self.tables:
            raise KeyError
        self.tables[name] = Table(name)

    def remove_table(self, name):
        if name not in self.tables:
            raise KeyError
        del self.tables[name]

    def get_all_tables(self):
        return self.tables.keys()

    def __repr__(self):
        tables_str = ', '.join(
            [f'"{table_name}": {table}' for table_name, table in self.tables.items()])
        return f'{{ {tables_str} }}'

    def print_json(self):
        print(json.dumps({self.name: json.loads(str(self))}, indent=2))


def title(self, message=None, decoration='<<< ERROR >>>'):
    line('=')
    center("Welcome to Table Mate")
    line('=')
    if message:
        message = str(message).strip('"')
        center(f"{message}", decoration=decoration)
        line('-')
    if self:
        self.print_json()
        line('-')


def clear(data=None, message=None, decoration=' '):
    if CLEAR:
        _ = os.system('cls') if os.name == 'nt' else os.system('clear')
        title(data, message, decoration)
    else:
        line('-')
        if message:
            line('*')
            print(message)
            line('*')
    return None


def line(char):
    print(char * math.floor(MENU_WIDTH / len(char)))


def center(message, decoration='', align='center', side='both'):
    margin = math.floor((MENU_WIDTH - len(message)) / 2)
    decoration_padding = " " * math.floor((margin - len(decoration)) / 2)
    margin_left = f'{decoration_padding if align != "outer" else decoration}{decoration_padding if align != "center" else decoration}{decoration_padding if align != "inner" else decoration}'
    margin_right = f'{decoration_padding if align != "inner" else decoration}{decoration_padding if align != "center" else decoration}{decoration_padding if align != "outer" else decoration}'

    print(f'{margin_left if side != "right" else " "*margin}{message}{margin_right if side != "left" else " "*margin}')


def table_menu(database):
    error = None
    while True:
        clear(database)

        center("Table Menu")
        center("'[c]reate' - Create a table")
        center("'[d]elete' - Delete a table")
        center("'[s]elect' - Select a table")
        center("'[SUBMIT]' - Submit Changes")
        line('-')
        option = input("Enter an option: ") if database.tables else "create"
        clear(database)
        if not option:
            return None
        elif option.lower() in ["create", "c"]:
            while True:
                error = clear(database, error, "<<< ERROR >>>")
                center("Create a table")
                table_name = input("Enter a table name: ")
                if not table_name:
                    break
                try:
                    database.add_table(table_name)
                    return table_name
                except Exception:
                    error = f"Table '{table_name}' already exists."
        elif option.lower() in ["delete", "d"] and database.tables:
            while True:
                error = clear(database, error)
                center("Delete a table")
                table_name = input("Enter a table name: ")
                if not table_name:
                    break
                try:
                    database.remove_table(table_name)
                    break
                except Exception:
                    error = f"Table '{table_name}' does not exist."
        elif option.lower() in ["select", "s"] and database.tables:
            while True:
                error = clear(database, error)
                center("Select a table")
                table_name = input("Enter a table name: ")
                if not table_name:
                    break
                if table_name in database.get_all_tables():
                    return table_name
                else:
                    print("Table not found.")
        elif option in ["SUBMIT"] and database.tables:
            error = clear(database, error)
            center("Submit changes?", "<<< WARNING >>>")
            submit_confirmation = input("Enter 'Y' to submit changes: ")
            if submit_confirmation != "Y":
                break
            print("Changes submitted.")
            input()


def attribute_menu(table_name, database):
    # target_db is your target database
    table = database.tables[table_name]
    error = None
    while True:
        clear(table)
        center("Attribute Menu")
        print("1. Add an attribute")
        if table.attributes:
            print("2. Remove an attribute")
        line('-')
        option = input("Enter an option: ") if table.attributes else '1'
        clear(table)
        if not option:
            return None
        elif option == "1":
            help_toggle = False
            while True:
                clear(table, error)
                center("Add attributes")
                center("{attribute} {type} {modifiers}", "<<< Format >>>")
                center("Type '?' to toggle a list of types.")
                line('-')
                if help_toggle:
                    type_menu()
                attr = input("Enter an attribute: ")
                if attr == "?":
                    help_toggle = not help_toggle
                    continue
                if not attr:
                    return
                try:
                    error = None
                    table.add_attribute(attr)
                except Exception as e:
                    error = (
                        f"Invalid attribute: '{attr}' ({e})")
        elif option == "2":
            while True:
                clear(table, error)
                center("Remove an attribute")
                attr_name = input("Enter an attribute name: ")
                if not attr_name:
                    break
                try:
                    table.remove_attribute(attr_name)
                except Exception:
                    error = f"Attribute '{attr_name}' does not exist."


def type_menu():
    center("Attribute Types")
    print('''
        NULL > (null): Represents a null value (no value).
        INTEGER > (int, integer): Represents a whole number (integer).
        REAL > (real): Represents a floating-point number (decimal).
        TEXT > (text, txt): Represents a string of characters (text).
        BLOB > (blob): Represents binary data (such as images or files).
        ''')
    center("Type Modifiers")
    print('''
        PRIMARY KEY > (pk): Specifies the attribute as the primary key for the table.
        FOREIGN KEY > (fk): Specifies a foreign key relationship between tables.
        REFERENCES > (ref): Specifies a reference to another table and column.
        ON DELETE > (od): Specifies the action to be taken when the referenced record is deleted.
        ON UPDATE > (ou): Specifies the action to be taken when the referenced record is updated.
        AUTOINCREMENT > (ai): Automatically increments the attribute's value for each new record.
        COLLATE > (co): Specifies the collation order for string comparison.
        CHECK > (ch): Specifies a condition that values must meet.
        NOT NULL > (nn): Specifies that the attribute cannot have a null value.
        UNIQUE > (u): Specifies that the attribute values must be unique.
        DEFAULT > (d): Specifies a default value for the attribute.
    ''')
    line('-')


def main():
    clear()

    while True:
        dirs = os.listdir("./db/")
        clear(None, dirs, "<< Available Databases >>")
        db_name = input("Enter a database name: ")
        if not db_name:
            break
        elif f"{db_name}.db" not in dirs:
            option = input("Would you like to create this database? (y/n): ")
            if option.lower() != "y":
                continue
        conn = sqlite3.connect(f"./db/{db_name}.db")
        database = Database(db_name, conn)
        if cursor := conn.cursor():
            while True:
                table_name = table_menu(database)
                if not table_name:
                    break
                while True:
                    attribute = attribute_menu(table_name, database)
                    if not attribute:
                        break
    cursor.close()
    conn.close()


main()
