 #? Title: gen_tree.py
 # Author: Harper Chisari

#? Contents:
#   CLASS - Gen_Tree: Contains all algorithmic transformations and pre-processing for a sheet
#       #!LAST TESTED: 8/16/23
#       METHOD - __init__: Initializes a Gen_Tree object with sheets and json_data
#       METHOD - __iter__: Iterated representation of the tree
#       METHOD - __str__: String representation of the tree
#       METHOD - __repr__: String representation of the tree
#       METHOD - check_df_ep: Checks if a DataFrame has a compatible data structure, returns the difference
#       METHOD - to_json: Serializes the tree into a JSON format
#       METHOD - to_clean_json: Serializes the tree into a readable JSON format
#       METHOD - get_unenclosed_tables: Returns all unenclosed tables in all the sheets
#       METHOD - get_prime_width_tables: Returns all the tables in all the sheets that have a prime number of columns

#? Version History:
# Version History:
#   Harper: 8/17/23 - V1.3 - redid title block
#   Dana: 7/24/23 - V1.2 - added __iter__ method


import json
import sys


if 'pytest' in sys.modules:
    from src.python.structures.sheet import Sheet as Sheet
    from src.python.structures.table import Table as Table
else:
    from structures.sheet import Sheet as Sheet


class Gen_Tree:
    def __init__(self, sheets=None, json_data=None):
        # The tree can be initialized either with a list of sheets or a dict of sheets
        if json_data:
            self.data = json.loads(json_data)
            self.sheets = {
                (Sheet(sheet).name, [Table(json_data=table_data) for table_data in Sheet(sheet).tables])
                for sheet in self.data }
        else:
            self.sheets = sheets if isinstance(sheets, dict) or not sheets else {
                sheet_instance.name: sheet_instance for sheet_instance in sheets}
            self.data = self.to_json()
        self.clean_data = self.to_clean_json()

    # Iterated representation of the tree
    def __iter__(self):
        if isinstance(self.sheets, dict):
            return iter(self.sheets.values())
        elif isinstance(self.sheets, list):
            return iter(self.sheets)

    # String representation of the tree
    def __str__(self):
        return str(self.to_clean_json())

    # String representation of the tree
    def __repr__(self):
        return str(self.to_clean_json())

    # Checks if a DataFrame has a compatible data structure, returns the difference
    def check_df_ep(self, df):
        mismatches = {}
        for sheet in self.sheets:
            mismatches[sheet.name] = sheet.checl_df_ep(df)
        return mismatches

    # Serializes the tree into a JSON format
    def to_json(self):
        json_out = {}
        for sheet in self.sheets.values():
            json_out.update(sheet.to_json())
        return json_out

    # Serializes the tree into a readable JSON format
    def to_clean_json(self):
        json_out = {}
        for sheet in self.sheets.values():
            sheet: Sheet
            json_out.update(sheet.to_clean_json())
        return json_out

    # Returns all unenclosed tables in all the sheets
    def get_unenclosed_tables(self):
        unenclosed_tables = []
        for sheet in self.sheets.values():
            sheet: Sheet
            unenclosed_tables.extend(sheet.get_unenclosed_tables())
        return unenclosed_tables

    # Returns all the tables in all the sheets that have a prime number of columns
    def get_prime_width_tables(self):
        prime_width_tables = []
        for sheet in self.sheets.values():
            sheet: Sheet
            prime_tables, dimensions = sheet.get_prime_tables()
            for table, dimension in zip(prime_tables, dimensions):
                if dimension[0] == 0:  # If the width is prime.
                    prime_width_tables.append(table)
        return prime_width_tables