import json
import re
import sys
#import csv

class cell:
    def __init__(self, location: tuple, value=" ", annotation="EMPTY") -> None:
        self.value = value
        self.annotation = annotation
        if self.annotation == "FOMRULA":
            self.block_type = "DATA"
        else:
            self.block_type = self.annotation
        if isinstance(location, str):
            self.coord_string = location
            if re.match(r"\(\s*\d+\s*,\s*\d+\s*\)", self.coord_string):
                self.coord = tuple(map(int, self.coord_string.replace("(", "").replace(")", "").split(', ')))
            else:
                self.coord_num()
        elif isinstance(location, tuple):
            self.coord = location
        else:
            raise ValueError(f"Invalid Cell coordinate: expected tuple or 'A1' format, got {location}")

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

    def to_json(self):
        return {"coord": self.coord, "value": self.value, "annotation": self.annotation}
    
    @classmethod
    def from_json(cls, json_data, coord):
        if not coord:
            coord = json_data.get("coord")
        value = json_data.get("value")
        annotation = json_data.get("annotation")
        return cls(coord, value, annotation)



class block:
    def __init__(self, cells: list[cell]=[], annotation_type=None):
        self.cells = cells
        if len(cells) < 1:
            raise ValueError("Invalid block size, need at least one cell")
        self.get_corners()
        if annotation_type:
            self.annotation_type = annotation_type
        else:
            self.get_annotation_type()
        self.check_consistancy()
        self.csv_format()
        self.expected_position = self.corners[0]
    
    def to_json(self):
        cells_dict = {"("+str(cell.coord[0]) + ', ' + str(cell.coord[1])+")": {"value": cell.value, "annotation": cell.annotation} for cell in self.cells}
        block_json = {
            "start": "("+str(self.corners[0][0]) + ', ' + str(self.corners[0][1])+")",
            "end": "("+str(self.corners[1][0]) + ', ' + str(self.corners[1][1])+")",
            "cells": cells_dict,
            "size": "("+str(self.size[0]) + ', ' + str(self.size[1])+")",
        }
        return block_json


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

    def check_consistancy(self):
        for cell in self.cells:
            if self.annotation_type == cell.block_type:
                pass
            else:
                raise ValueError(f"Inconsistent block type, expecting type {self.annotation_type}, found cell with {cell.block_type}")

    def get_annotation_type(self):
        first_cell = self.cells[0]
        self.annotation_type = first_cell.block_type

    def csv_format(self):
        csv_rows = []
        for cell in self.cells:
            csv_row = [cell.coord[0], cell.coord[1], cell.value, cell.annotation]
            csv_rows.append(csv_row)
        
        csv_string = ''
        if len(csv_rows) > 0:
            csv_string = '\n'.join([','.join(map(str, row)) for row in csv_rows])
        
        self.csv_data = csv_string

    def get_relative_position(self, origin: tuple):
        #gets relative position of top left corner based on a given origin
        relative_position = []
        for dimension in [0,1]:
            relative_position.append(self.expected_position[dimension] - origin[dimension])
        self.relative_position = tuple(relative_position)
        return self.relative_position
    
    @classmethod
    def from_json(cls, json_data):
        return cls(cells=[cell.from_json(cell_data, coord) for coord, cell_data in json_data["cells"].items()]) if json_data else None


class table:
    def __init__(self, expected_position=(0,0), free_labels=[],free_data=[],subtables=[],l0=None, l1=None, r0=None, r1=None, t0=None, t1=None, b0=None, b1=None, data_block=None, json_data = None):
        self.data_block = data_block
        self.label_blocks = {"same_height": {"l0": l0, "l1": l1, "r0": r0, "r1": r1}, "same_width": {"t0": t0, "t1": t1, "b0": b0, "b1": b1}}
        self.subtables = subtables
        self.free_blocks = {"lable_blocks":free_labels,"data_blocks":free_data}
        self.get_size()
        self.expected_position = expected_position


    def is_enclosed(self):
        #checks whether there is a same_height and same_width label block
        return any(value is not None for value in self.label_blocks["same_height"].values()) and any(value is not None for value in self.label_blocks["same_width"].values())


    def is_prime(self):
        # checks if the size of the data block is prime, returns None, Horizontal, or Vertical
        dims = []
        if self.data_block is None: return None  # Add a check if data_block is None

        for dimension in [0,1]:
            dim = self.data_block.size[dimension]
            if dim < 2:
                continue
            for divisor in range(2, int(dim ** 0.5) + 1):
                if dim % divisor == 0:
                    break
            else:
                dims.append(dimension) # Indent to correct level
                
        return dims if dims else None # Check if dims is empty instead of indexing


    def get_relative_position(self, origin: tuple):
        #gets relative position of top left corner based on a given origin
        relative_position = []
        for dimension in [0,1]:
            relative_position.append(self.expected_position[dimension] - origin[dimension])
        self.relative_position = tuple(relative_position)
        return self.relative_position

    def get_child_rel_pos(self):
        if self.data_block:
            self.data_block.get_relative_position(self.expected_position) 
        for dim in ["same_height", "same_width"]:
            for block in self.label_blocks[dim].values():
                if block:
                    block.get_relative_position(origin = self.expected_position)
        for table in self.subtables:
            table.get_relative_position(origin = self.expected_position)


    def get_size(self):
        print(self.free_blocks)
        total_size = list(self.data_block.size)  # Make a copy of the size
        offsets = [[["same_height", "l0"], [1,0]], [["same_height","l1"], [2,0]], [["same_height","r0"], [1,0]], [["same_height","r1"], [2,0]], [["same_width","t0"], [0,1]], [["same_width","t1"], [0,2]], [["same_width","b0"], [0,1]], [["same_width","b1"], [0,2]]]
        for offset in offsets:
            block = self.label_blocks[offset[0][0]][offset[0][1]]
            if block:
                for coord in [0,1]:
                    #print(offset)
                    total_size[coord] += offset[1][coord]
        self.expected_size = tuple(total_size)

    def to_json(self):
        data_block_json = self.data_block.to_json() if self.data_block else None

        label_blocks_json = {
            outer_key: {inner_key: inner_value if inner_value else None 
                        for inner_key, inner_value in outer_value.items()} 
            for outer_key, outer_value in self.label_blocks.items()
        }

        subtables_json = [subtable.to_json() for subtable in self.subtables]

        print(self.free_blocks)
        free_label_blocks_json = [block.to_json() for block in self.free_blocks["lable_blocks"]]
        free_data_blocks_json = [block.to_json() for block in self.free_blocks["data_blocks"]]

        table_json = {
            "data_block": data_block_json,
            "label_blocks": label_blocks_json,
            "subtables": subtables_json,
            "free_blocks": {"LABEL": free_label_blocks_json, "DATA": free_data_blocks_json},
            "size": "("+str(self.expected_size[0]) + ', ' + str(self.expected_size[1])+")",
            "start": "("+str(self.expected_position[0]) + ', ' + str(self.expected_position[1])+")",
        }

        return table_json
    
    @classmethod
    def from_json(cls, json_data):
        # Assuming block class has a from_json method that handles None
        label_blocks = {"same_height": {"l0": block.from_json(json_data.get("l0")),
                                        "l1": block.from_json(json_data.get("l1")),
                                        "r0": block.from_json(json_data.get("r0")),
                                        "r1": block.from_json(json_data.get("r1"))},
                        "same_width": {"t0": block.from_json(json_data.get("t0")),
                                    "t1": block.from_json(json_data.get("t1")),
                                    "b0": block.from_json(json_data.get("b0")),
                                    "b1": block.from_json(json_data.get("b1"))}}
        subtables = [cls.from_json(subtable_data) for subtable_data in json_data.get("subtables", [])]
        free_labels = [block.from_json(block_data) for block_data in json_data.get("free_blocks", {}).get("LABEL", [])]
        free_data = [block.from_json(block_data) for block_data in json_data.get("free_blocks", {}).get("DATA", [])]
        expected_position = tuple(json_data.get("expected_position", (0,0)))
        expected_size = tuple(json_data.get("expected_size", (0,0)))
        data_block = block.from_json(json_data.get("data_block")) if json_data.get("data_block") else None
        return cls(expected_position, expected_size, free_labels, free_data, subtables, label_blocks, data_block=data_block)

class Sheet:
    def __init__(self, name, tables=[]):
        self.name = name
        self.tables = tables

    def to_csv(self):
        csv_data = [table.data_block.csv_data for table in self.tables]
        return "\n".join(csv_data)

    def to_json(self):
        tables_json = [table.to_json() for table in self.tables]
        sheet_json = {
            "name": self.name,
            "tables": tables_json
        }
        return sheet_json

    def get_unenclosed_tables(self):
        unenclosed_tables = [table for table in self.tables if not table.is_enclosed()]
        return unenclosed_tables

    def get_prime_tables(self):
        prime_tables = [table for table in self.tables if table.is_prime() is not None]
        return prime_tables, [table.is_prime() for table in prime_tables if table.is_prime() is not None]

class gen_tree:
    def __init__(self, sheets=None, json_data=None):
        if json_data:
            self.data = json.loads(json_data)
            # Assuming that the JSON data is a list of sheet JSONs.
            self.sheets = [Sheet(sheet_data["name"], [table(json_data=table_data) for table_data in sheet_data["tables"]]) for sheet_data in self.data]
        else:
            self.sheets = sheets or []
            self.data = [sheet.to_json() for sheet in self.sheets]

    def cleaned_hierarchy_output(self):
        # Assuming this method is supposed to pretty print the tree.
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
        # Rebuilds the JSON data from the sheets and their contained tables.
        self.data = [sheet.to_json() for sheet in self.sheets]
        return json.dumps(self.data)

    def get_unenclosed_tables(self):
        unenclosed_tables = []
        for sheet in self.sheets:
            unenclosed_tables.extend(sheet.get_unenclosed_tables())
        return unenclosed_tables

    def get_prime_width_tables(self):
        prime_width_tables = []
        for sheet in self.sheets:
            prime_tables, dimensions = sheet.get_prime_tables()
            for table, dimension in zip(prime_tables, dimensions):
                if dimension[0] == 0:  # If the width is prime.
                    prime_width_tables.append(table)
        return prime_width_tables