"""
Version:                2.0
Last Edit:              7/24/2023
Last Author:            Dana Solitaire
"""

class Gen_Tree:
    def __init__(self, sheets=None, json_data=None):
        # The tree can be initialized either with a list of sheets or a dict of sheets
        """ if json_data:
            self.data = json.loads(json_data)
            self.sheets = [sheet(sheet_data["name"], 
                [table(json_data=table_data) for table_data in sheet_data["tables"]]) 
                for sheet_data in self.data] """
        
        self.sheets = sheets if isinstance(sheets, dict) or not sheets else {
            sheet_instance.name: sheet_instance for sheet_instance in sheets}
        self.data = self.to_json()
        self.clean_data = self.to_clean_json()

    def __iter__(self):
        if isinstance(self.sheets, dict):
            return iter(self.sheets.values())
        elif isinstance(self.sheets, list):
            return iter(self.sheets)
    
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
        return json_out

    def to_clean_json(self):
        # Converts the tree back to a JSON format
        json_out = {}
        for sheet in self.sheets.values():
            json_out.update(sheet.to_clean_json())
        return json_out

    def get_unenclosed_tables(self):
        # Returns al l the unenclosed tables in all the sheets
        unenclosed_tables = []
        for sheet in self.sheets.keys():
            unenclosed_tables.append(self.sheets.get(sheet))
        return unenclosed_tables

    def get_prime_width_tables(self):
        # Returns all the tables in all the sheets that have a prime number of columns
        prime_width_tables = []
        for sheet in self.sheets.keys():
            current_sheet = self.sheets.get(sheet)
            prime_tables, dimensions = current_sheet
            for table, dimension in zip(prime_tables, dimensions):
                if dimension[0] == 0:  # If the width is prime.
                    prime_width_tables.append(table)
        return prime_width_tables