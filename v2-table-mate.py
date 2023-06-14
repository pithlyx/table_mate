import json
import math
import os
import curses

CLEAR = False
CLEAR = True
MENU_WIDTH = 100


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
    def __init__(self, name):
        self.name = name
        self.tables = {}

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


class SQL:
    def __init__(self):
        self.databases = {}

    def add_database(self, name):
        if name in self.databases:
            raise KeyError
        self.databases[name] = Database(name)

    def remove_database(self, name):
        print(name)
        print(self.databases)
        if name not in self.databases:
            raise KeyError
        del self.databases[name]

    def get_all_databases(self):
        return self.databases.keys()

    def __repr__(self):
        databases_str = ', '.join(
            [f'"{db_name}": {db}' for db_name, db in self.databases.items()])
        return f'{{ "databases": {{ {databases_str} }} }}'

    def print_json(self):
        print(json.dumps(json.loads(str(self)), indent=2))


def title(self, error=None):
    line('=')
    center("Welcome to Table Mate")
    line('=')
    if error:
        error = str(error).strip('"')
        center(f"{error}", "<<< ERROR >>>")
        line('-')
    if self:
        self.print_json()
        line('-')


def clear(data=None, error=None):
    if CLEAR:
        _ = os.system('cls') if os.name == 'nt' else os.system('clear')
        title(data, error)
    else:
        line('-')
        if error:
            line('*')
            print(error)
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


sql = SQL()


def sql_menu():
    error = None
    while True:
        clear(sql, error)
        error = None
        center("Database Menu")
        print("1. Create a database")
        if sql.databases:
            print("2. Delete a database")
            print("3. Select a Database")
        line('-')
        option = input("Enter an option: ") if sql.databases else "1"
        clear(sql)
        if not option:
            exit_opt = input("Would you like to exit? (y/n): ")
            if exit_opt == "y":
                exit()
        elif option == "1":
            while True:
                error = clear(sql, error)
                center("Create a database")
                db_name = input("Enter a database name: ")
                if not db_name:
                    break
                try:
                    sql.add_database(db_name)
                    break
                except Exception:
                    error = (f"Database '{db_name}' already exists.")
            return db_name
        elif option == "2" and sql.databases:
            while True:
                error = clear(sql, error)
                center("Delete a database")
                db_name = input("Enter a database name: ")
                if not db_name:
                    break
                try:
                    sql.remove_database(db_name)
                    break
                except Exception:
                    error = f"Database '{db_name}' does not exist."
        elif option == "3" and sql.databases:
            while True:
                error = clear(sql, error)
                center("Select a database")
                db_name = input("Enter a database name: ")
                if not db_name:
                    break
                if db_name in sql.get_all_databases():
                    return db_name
                else:
                    error = ("Database not found.")
        else:
            error = ("Invalid option.")


def database_menu(db_name):
    database = sql.databases[db_name]
    error = None
    while True:
        clear(database)
        center("Table Menu")
        print("1. Create a table")
        if database.tables:
            print("2. Select a table")
            print("3. Delete a table")
        line('-')
        option = input("Enter an option: ") if database.tables else "1"
        clear(database)
        if not option:
            return
        elif option == "1":
            while True:
                error = clear(database, error)
                center("Create a table")
                table_name = input("Enter a table name: ")
                if not table_name:
                    break
                try:
                    database.add_table(table_name)
                    return table_name
                except Exception:
                    error = f"Table '{table_name}' already exists."
        elif option == "2" and database.tables:
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
        elif option == "3" and database.tables:
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


def table_menu(db_name, table_name):
    table = sql.databases[db_name].tables[table_name]
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
            return
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
                    break
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
        if db_name := sql_menu():
            if table_name := database_menu(db_name):
                table_menu(db_name, table_name)


sql = SQL()
main()
