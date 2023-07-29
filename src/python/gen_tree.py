"""
Version:                2.0
Last Edit:              7/24/2023
Last Author:            Dana Solitaire
"""

class Gen_Tree:
    def __init__(self, sheets=None):
        # The tree can be initialized either with a list of sheets or a dict of sheets
        self.sheets = sheets if isinstance(sheets, dict) or not sheets else {
            sheet_instance.name: sheet_instance for sheet_instance in sheets}

    def __str__(self):
        return str(self.to_clean_json())

    def __repr__(self):
        return str(self.to_clean_json())
    
    def check_df_ep(self, df):
        mismatches = {}
        for sheet in self.sheets:
            mismatches[sheet.name] = sheet.checl_df_ep(df)
        return mismatches

    def to_json(self):
        # Converts the tree back to a JSON format
        json_out = {}
        for sheet in self.sheets.values():
            json_out.update(sheet.to_json())
        self.data = json_out
        return self.data

    def to_clean_json(self):
        # Converts the tree back to a JSON format
        json_out = {}
        for sheet in self.sheets.values():
            json_out.update(sheet.to_clean_json())
        self.clean_data = json_out
        return self.clean_data

    def get_unenclosed_tables(self):
        # Returns all the unenclosed tables in all the sheets
        unenclosed_tables = []
        for sheet in self.sheets:
            unenclosed_tables.extend(sheet.get_unenclosed_tables())
        return unenclosed_tables

    def get_prime_width_tables(self):
        # Returns all the tables in all the sheets that have a prime number of columns
        prime_width_tables = []
        for sheet in self.sheets:
            prime_tables, dimensions = sheet.get_prime_tables()
            for table, dimension in zip(prime_tables, dimensions):
                if dimension[0] == 0:  # If the width is prime.
                    prime_width_tables.append(table)
        return prime_width_tables