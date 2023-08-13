import sys
import pandas as pd


# Title: sheet.py
# Author: Harper Chisari
# Description: Defines the Sheet class, representing a sheet containing tables, free labels, free data, cells, and blocks. Provides methods for DataFrame validation, CSV and JSON serialization, block retrieval, and special table analysis.
# Contents:
#   CLASS - Sheet:
#       METHOD - __init__: Initializes a Sheet object with name, tables, free labels, free data, cells, and blocks
#       METHOD - __str__: String representation of the Sheet object
#       METHOD - __repr__: String representation of the Sheet object
#       METHOD - to_dataframe: Builds a DataFrame representation of the sheet by inserting DataFrames for all blocks, tables, free_labels, and free_data blocks using the relative expected_position
#       METHOD - check_df_ep: Checks if a DataFrame has a compatible data structure
#       METHOD - get_blocks: Retrieves all blocks within the sheet
#       METHOD - get_csv: Builds a CSV representation of all cells in the sheet
#       METHOD - to_csv: Converts the data in the tables to a CSV format
#       METHOD - to_json: Serializes the sheet object into a JSON format
#       METHOD - to_clean_json: Represents the Sheet in a cleaner JSON format
#       METHOD - get_unenclosed_tables: Returns the tables that are not enclosed by labels
#       METHOD - get_prime_tables: Returns the tables that have a prime number of rows or columns
#       METHOD - from_json: Creates a Sheet object from JSON data

# Version History:
#   Harper: 8/13/23 - V1.3 - Added title block, to_dataframe method

if 'pytest' in sys.modules:
    from src.python.structures.utilities import Gen_Tree_Helper as gth
    from src.python.structures.cell import Cell as cel
    from src.python.structures.block import Block as blk
    from src.python.structures.table import Table as tbl
else:
    from structures.utilities import Gen_Tree_Helper as gth
    from structures.cell import Cell as cel
    from structures.block import Block as blk
    from structures.table import Table as tbl

class Sheet:
    def __init__(self, name, tables=[], free_labels=[], free_data=[], cells=None, blocks=None):
        self.name = name  # The name of the sheet
        self.cells = cells
        self.blocks = blocks
        self.tables = tables  # The tables in the sheet
        self.free_labels = free_labels
        self.free_data = free_data
        if self.cells:
            self.blocks = []
            for cell in self.cells:
                if cell.annotation == 'EMPTY':
                    continue
                block = blk.block(cells=[cell])
                self.blocks.append(block)
        if self.blocks:
            for block in self.blocks:
                if block.annotation_type == "LABEL":
                    self.free_labels.append(block)
                if block.annotation_type == "DATA":
                    self.free_data.append(block)
        else:
            self.blocks = []
            self.blocks.extend(self.free_labels)
            self.blocks.extend(self.free_data)
        
        self.to_dataframe()

    def __str__(self):
        return str(self.to_json())
    
    def __repr__(self):
        return str("\n\tName:  {} \n\tCells: {} \n\tBlocks: {} \n\tTables: {} \n\tFree Labels: {} \n\tFree Data: {}").format(self.name, self.cells, self.blocks, self.tables, self.free_labels, self.free_data)

    def to_dataframe(self):
        # Create an empty DataFrame
        df = pd.DataFrame()

        # Iterate through all blocks, tables, free labels, and free data blocks
        for collection in [self.blocks, self.tables, self.free_labels, self.free_data]:
            for item in collection:
                expected_position = item.expected_position
                #gth.debug_print(f"Item EP: {expected_position} ")
                item_df = item.to_dataframe()

                # Insert the item DataFrame into the main DataFrame at the relative expected position
                #gth.debug_print(f"Dataframe: \n {item_df}")
                df = gth.insert_dataframe(df, item_df, expected_position)
        self.dataframe = df
        gth.debug_print(f"Sheet Dataframe: \n {df}")
        return self.dataframe

    def check_df_ep(self, df):
        # Initialize a dictionary to store the mismatches
        mismatches = {}

        # Check for mismatches in the free labels
        for free_label in self.free_labels:
            free_label_check_result = free_label.check_df_ep(df)
            if free_label_check_result != True:
                # If there are mismatches, update the mismatches dictionary
                mismatches.update(free_label_check_result)

        # Check for mismatches in the free data blocks
        for free_data_block in self.free_data:
            free_data_check_result = free_data_block.check_df_ep(df)
            if isinstance(free_data_check_result, dict):
                for coord, value in free_data_check_result.items():
                    cell = next((cell for cell in free_data_block.cells if cell.coord == coord), None)
                    if cell is not None:
                        cell.value = value

        # Check for mismatches in all tables
        for table in self.tables:
            table_check_result = table.check_df_ep(df)
            if table_check_result != True:
                # If there are mismatches, update the mismatches dictionary
                mismatches.update({table.expected_position: table_check_result})

        # Return the mismatches dictionary
        return mismatches
    
    def get_blocks(self):
        self.all_blocks = []
        for table in self.tables:
            self.all_blocks.table.get_blocks()
        for block_list in [self.free_labels, self.free_data]:
            self.all_blocks += block_list

    def get_csv(self):
        self.get_blocks()
        all_cells = []
        for Block in self.all_blocks:
            all_cells += Block.cells
        return gth.build_csv(cells=all_cells)

    def to_csv(self):
        # Converts the data in the tables to a CSV format
        csv_data = [table.data_block.csv_data for table in self.tables]
        return "\n".join(csv_data)

    def to_json(self):
        # Converts the sheet to a JSON format
        tables_json = [table.to_json() for table in self.tables]
        free_label_blocks_json = [block.to_json()
                                  for block in self.free_labels]
        free_data_blocks_json = [block.to_json() for block in self.free_data]
        sheet_json = {self.name: {"tables": tables_json,
                                  "free_labels": free_label_blocks_json,
                                  "free_data": free_data_blocks_json}}
        return sheet_json

    def to_clean_json(self):
        # Converts the sheet to a JSON format
        tables_clean_json = [table.to_clean_json() for table in self.tables]
        free_label_blocks_clean_json = [
            block.to_clean_json() for block in self.free_labels]
        free_data_blocks_clean_json = [
            block.to_clean_json() for block in self.free_data]
        sheet_clean_json = {self.name: {"tables": tables_clean_json,
                                        "free_blocks": free_label_blocks_clean_json + free_data_blocks_clean_json}}
        return sheet_clean_json

    def get_unenclosed_tables(self) -> list:
        # Returns the tables that are not enclosed by labels from both dimensions
        unenclosed_tables = [
            table for table in self.tables if not table.is_enclosed()]
        return unenclosed_tables

    def get_prime_tables(self) -> list:
        # Returns the tables that have a prime number of rows or columns
        prime_tables = [
            table for table in self.tables if table.is_prime() is not None]
        return prime_tables, [table.is_prime() for table in prime_tables if table.is_prime() is not None]

    def from_json(cls, json_data):
        # Converts the json to a sheet
        AssertionError(len(json_data) != 1, "")
        for name, sheet in json_data.items():
            return Sheet(name, json_data.get("tables", []), json_data.get("free_labels", []), json_data.get("free_data", []), json_data.get("tables", []).get("cells"))