import json
import re
import sys

# Class to represent a single cell in the grid
class cell:
    def __init__(self, location: tuple, value=" ", annotation="EMPTY") -> None:
        # Set the cell value and annotation (default is 'EMPTY')
        self.value = value
        self.annotation = annotation
        # Define block type based on annotation
        if self.annotation == "FOMRULA":
            self.block_type = "DATA"
        else:
            self.block_type = self.annotation
        # Handle coordinates in different formats
        if isinstance(location, str):
            self.coord_string = location
            # If string matches the pattern of a tuple of integers, convert it to tuple
            if re.match(r"\(\s*\d+\s*,\s*\d+\s*\)", self.coord_string):
                self.coord = tuple(map(int, self.coord_string.replace("(", "").replace(")", "").split(', ')))
            else:
                self.coord_num()
        elif isinstance(location, tuple):
            self.coord = location
        else:
            raise ValueError(f"Invalid Cell coordinate: expected tuple or 'A1' format, got {location}")

    # Function to convert Excel-like coordinates (e.g., 'A1') to numeric coordinates
    def coord_num(self):
        match = re.match(r'([A-Z]+)(\d+)', self.coord_string)
        if not match:
            raise ValueError(f"Invalid Excel coordinate, expected 'A1' format, got {self.coord_string}")

        column = match.group(1)
        row = int(match.group(2))

        # Convert column to x coordinate
        x = 0
        for i, char in enumerate(reversed(column)):
            # Convert character to ASCII code and subtract 64 to get its corresponding column number
            column_num = ord(char) - 64
            x += column_num * (26 ** i)

        # Convert row to y coordinate
        y = row

        self.coord = (x,y)

    # Function to serialize the cell object into a JSON format
    def to_json(self):
        return {"coord": self.coord, "value": self.value, "annotation": self.annotation}

    # Class method to create a cell object from a JSON data
    @classmethod
    def from_json(cls, json_data, coord):
        if not coord:
            coord = json_data.get("coord")
        value = json_data.get("value")
        annotation = json_data.get("annotation")
        return cls(coord, value, annotation)

# Class to represent a block of cells in the grid
class block:
    def __init__(self, cells: list[cell]=[], annotation_type=None):
        self.cells = cells
        # Ensure that there is at least one cell in the block
        if len(cells) < 1:
            raise ValueError("Invalid block size, need at least one cell")
        # Calculate corners and size of the block
        self.get_corners()
        if annotation_type:
            self.annotation_type = annotation_type
        else:
            self.get_annotation_type()
        # Ensure that all cells in the block are consistent in type
        self.check_consistancy()
        # Format block data into a CSV format
        self.csv_format()
        self.expected_position = self.corners[0]

    # Function to serialize the block object into a JSON format
    def to_json(self):
        # Represent cells as a dictionary, where keys are their coordinates
        cells_dict = {"("+str(cell.coord[0]) + ', ' + str(cell.coord[1])+")": {"value": cell.value, "annotation": cell.annotation} for cell in self.cells}
        block_json = {
            "start": "("+str(self.corners[0][0]) + ', ' + str(self.corners[0][1])+")",
            "end": "("+str(self.corners[1][0]) + ', ' + str(self.corners[1][1])+")",
            "cells": cells_dict,
            "size": "("+str(self.size[0]) + ', ' + str(self.size[1])+")",
        }
        return block_json

    # Function to find the smallest and largest coordinates of cells in the block, effectively finding the corners
    def get_corners(self):
        max_coord = [float('-inf'), float('-inf')]
        min_coord = [float('inf'), float('inf')]
        for cell in self.cells:
            for direction in [0,1]:
                if cell.coord[direction] > max_coord[direction]:
                    max_coord[direction] = cell.coord[direction]
                if cell.coord[direction] < min_coord[direction]:
                    min_coord[direction] = cell.coord[direction]
        self.corners = (tuple(min_coord),tuple(max_coord))
        self.size = (int(self.corners[1][0]) - int(self.corners[0][0]), int(self.corners[1][1]) - int(self.corners[0][1]))

    # Function to check if all cells in the block are of the same type as the block
    def check_consistancy(self):
        for cell in self.cells:
            if self.annotation_type == cell.block_type:
                pass
            else:
                raise ValueError(f"Inconsistent block type, expecting type {self.annotation_type}, found cell with {cell.block_type}")

    # Function to get the annotation type of the block
    def get_annotation_type(self):
        first_cell = self.cells[0]
        self.annotation_type = first_cell.block_type

    # Function to convert block data into CSV format
    def csv_format(self):
        csv_rows = []
        for cell in self.cells:
            csv_row = [cell.coord[0], cell.coord[1], cell.value, cell.annotation]
            csv_rows.append(csv_row)
        
        csv_string = ''
        if len(csv_rows) > 0:
            csv_string = '\n'.join([','.join(map(str, row)) for row in csv_rows])
        
        self.csv_data = csv_string

    # Function to get the position of the block relative to an origin
    def get_relative_position(self, origin: tuple):
        #gets relative position of top left corner based on a given origin
        relative_position = []
        for dimension in [0,1]:
            relative_position.append(self.expected_position[dimension] - origin[dimension])
        self.relative_position = tuple(relative_position)
        return self.relative_position
    
    # Class method to create a block object from a JSON data
    @classmethod
    def from_json(cls, json_data):
        return cls(cells=[cell.from_json(cell_data, coord) for coord, cell_data in json_data["cells"].items()]) if json_data else None
class table:
    def __init__(self, expected_position=(0,0), free_labels=[],free_data=[],subtables=[],l0=None, l1=None, r0=None, r1=None, t0=None, t1=None, b0=None, b1=None, data_block=None, json_data = None):
        self.data_block = data_block  # The main data block of the table
        self.label_blocks = {"same_height": {"l0": l0, "l1": l1, "r0": r0, "r1": r1}, "same_width": {"t0": t0, "t1": t1, "b0": b0, "b1": b1}}  # The labels of the table
        self.subtables = subtables  # Any subtables inside the table
        self.free_blocks = {"lable_blocks":free_labels,"data_blocks":free_data}  # Any additional data or label blocks not classified yet
        self.get_size()  # Calculate the size of the table
        self.expected_position = expected_position  # The expected position of the table in the parent table or sheet

    def is_enclosed(self):
        # Checks if the table is enclosed by labels from both height and width dimensions
        return any(value is not None for value in self.label_blocks["same_height"].values()) and any(value is not None for value in self.label_blocks["same_width"].values())

    def is_prime(self):
        # Checks if the size of the data block is prime, returns None if not, else returns the dimensions that are prime
        dims = []
        if self.data_block is None: return None  # If there is no data block, return None

        for dimension in [0,1]:  # For each dimension of the data block
            dim = self.data_block.size[dimension]
            if dim < 2:  # If dimension is less than 2, it's not prime, so continue to next dimension
                continue
            for divisor in range(2, int(dim ** 0.5) + 1):  # Check if the dimension is divisible by any number up to its square root
                if dim % divisor == 0:  # If it is, break the loop and move on to next dimension
                    break
            else:
                dims.append(dimension)  # If not, then the dimension is prime, so add it to the dims list

        return dims if dims else None  # Return the prime dimensions if any, else return None

    def get_relative_position(self, origin: tuple):
        # Gets the relative position of the top left corner of the table based on a given origin
        relative_position = []
        for dimension in [0,1]:  # For each dimension
            relative_position.append(self.expected_position[dimension] - origin[dimension])
        self.relative_position = tuple(relative_position)
        return self.relative_position  # Returns the relative position

    def get_child_rel_pos(self):
        # Calculate the relative position for each child block and subtable
        if self.data_block:  # If there is a data block
            self.data_block.get_relative_position(self.expected_position)  # Calculate its relative position
        for dim in ["same_height", "same_width"]:  # For each dimension
            for block in self.label_blocks[dim].values():  # For each label block in the dimension
                if block:  # If the label block exists
                    block.get_relative_position(origin = self.expected_position)  # Calculate its relative position
        for table in self.subtables:  # For each subtable
            table.get_relative_position(origin = self.expected_position)  # Calculate its relative position

    def get_size(self):
        # Calculate the total size of the table
        print(self.free_blocks)
        total_size = list(self.data_block.size)  # Make a copy of the size of the data block
        offsets = [[["same_height", "l0"], [1,0]], [["same_height","l1"], [2,0]], [["same_height","r0"], [1,0]], [["same_height","r1"], [2,0]], [["same_width","t0"], [0,1]], [["same_width","t1"], [0,2]], [["same_width","b0"], [0,1]], [["same_width","b1"], [0,2]]]
        # Above offsets specify how the size of each label block contributes to the total size of the table

        for offset in offsets:
            block = self.label_blocks[offset[0][0]][offset[0][1]]
            if block:  # If the block exists
                for coord in [0,1]:  # For each dimension
                    total_size[coord] += offset[1][coord]  # Add the contribution of the block to the total size
        self.expected_size = tuple(total_size)  # Set the expected size

    def to_json(self):
        # Converts the table to a JSON format for easy saving and loading
        data_block_json = self.data_block.to_json() if self.data_block else None  # Convert the data block to JSON if it exists

        label_blocks_json = {
            outer_key: {inner_key: inner_value if inner_value else None 
                        for inner_key, inner_value in outer_value.items()} 
            for outer_key, outer_value in self.label_blocks.items()
        }  # Convert the label blocks to JSON

        subtables_json = [subtable.to_json() for subtable in self.subtables]  # Convert the subtables to JSON

        print(self.free_blocks)
        free_label_blocks_json = [block.to_json() for block in self.free_blocks["lable_blocks"]]  # Convert the free label blocks to JSON
        free_data_blocks_json = [block.to_json() for block in self.free_blocks["data_blocks"]]  # Convert the free data blocks to JSON

        table_json = {
            "data_block": data_block_json,
            "label_blocks": label_blocks_json,
            "subtables": subtables_json,
            "free_blocks": {"LABEL": free_label_blocks_json, "DATA": free_data_blocks_json},
            "size": "("+str(self.expected_size[0]) + ', ' + str(self.expected_size[1])+")",
            "start": "("+str(self.expected_position[0]) + ', ' + str(self.expected_position[1])+")",
        }  # Combine all the components into a JSON object

        return table_json  # Return the JSON object

    @classmethod
    def from_json(cls, json_data):
        # Reconstructs the table from a JSON object
        label_blocks = {"same_height": {"l0": block.from_json(json_data.get("l0")),
                                        "l1": block.from_json(json_data.get("l1")),
                                        "r0": block.from_json(json_data.get("r0")),
                                        "r1": block.from_json(json_data.get("r1"))},
                        "same_width": {"t0": block.from_json(json_data.get("t0")),
                                    "t1": block.from_json(json_data.get("t1")),
                                    "b0": block.from_json(json_data.get("b0")),
                                    "b1": block.from_json(json_data.get("b1"))}}
        # Above recreates the label blocks from JSON

        subtables = [cls.from_json(subtable_data) for subtable_data in json_data.get("subtables", [])]  # Recreates the subtables from JSON
        free_labels = [block.from_json(block_data) for block_data in json_data.get("free_blocks", {}).get("LABEL", [])]  # Recreates the free label blocks from JSON
        free_data = [block.from_json(block_data) for block_data in json_data.get("free_blocks", {}).get("DATA", [])]  # Recreates the free data blocks from JSON
        expected_position = tuple(json_data.get("expected_position", (0,0)))  # Gets the expected position from JSON
        expected_size = tuple(json_data.get("expected_size", (0,0)))  # Gets the expected size from JSON
        data_block = block.from_json(json_data.get("data_block")) if json_data.get("data_block") else None  # Recreates the data block from JSON

        return cls(expected_position, expected_size, free_labels, free_data, subtables, label_blocks, data_block=data_block)  # Returns the recreated table

class Sheet:
    def __init__(self, name, tables=[]):
        self.name = name  # The name of the sheet
        self.tables = tables  # The tables in the sheet

    def to_csv(self):
        # Converts the data in the tables to a CSV format
        csv_data = [table.data_block.csv_data for table in self.tables]
        return "\n".join(csv_data)

    def to_json(self):
        # Converts the sheet to a JSON format
        tables_json = [table.to_json() for table in self.tables]
        sheet_json = {
            "name": self.name,
            "tables": tables_json
        }
        return sheet_json

    def get_unenclosed_tables(self):
        # Returns the tables that are not enclosed by labels from both dimensions
        unenclosed_tables = [table for table in self.tables if not table.is_enclosed()]
        return unenclosed_tables

    def get_prime_tables(self):
        # Returns the tables that have a prime number of rows or columns
        prime_tables = [table for table in self.tables if table.is_prime() is not None]
        return prime_tables, [table.is_prime() for table in prime_tables if table.is_prime() is not None]

class gen_tree:
    def __init__(self, sheets=None, json_data=None):
        # The tree can be initialized either with a list of sheets or a JSON data of the sheets
        if json_data:
            self.data = json.loads(json_data)
            self.sheets = [Sheet(sheet_data["name"], [table(json_data=table_data) for table_data in sheet_data["tables"]]) for sheet_data in self.data]
        else:
            self.sheets = sheets or []
            self.data = [sheet.to_json() for sheet in self.sheets]

    def cleaned_hierarchy_output(self):
        # Prints the structure of the tree in a more readable format
        for sheet in self.sheets:
            print(f"Sheet: {sheet.name}")
            for table in sheet.tables:
                print(f"  Table at {table.expected_position} with size {table.expected_size}")
                if table.data_block:
                    print(f"    Data block at {table.data_block.expected_position} with size {table.data_block.size}")
                for label_blocks in table.label_blocks.values():
                    for label_block in label_blocks.values():
                        if label_block:
                            print(f"    Label block at {label_block.expected_position} with size {label_block.size}")
                for subtable in table.subtables:
                    print(f"    Subtable at {subtable.expected_position} with size {subtable.expected_size}")

    def to_json(self):
        # Converts the tree back to a JSON format
        self.data = [sheet.to_json() for sheet in self.sheets]
        return json.dumps(self.data)

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
