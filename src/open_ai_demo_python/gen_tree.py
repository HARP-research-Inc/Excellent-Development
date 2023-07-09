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

class block:
    def __init__(self, cells: list[cell], annotation_type=None):
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
        cells_dict = {str(cell.coord): {"value": cell.value, "annotation": cell.annotation} for cell in self.cells}
        block_json = {
            "start": str(self.corners[0]),
            "end": str(self.corners[1]),
            "cells": cells_dict,
            "size": str(self.size),
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

class table:
    def __init__(self, expected_position=(0,0), expected_size=(0,0),free_labels=[],free_data=[],subtables=[],l0=None, l1=None, r0=None, r1=None, t0=None, t1=None, b0=None, b1=None, data_block=None, json_data = None):
        self.data_block = data_block
        self.label_blocks = {"same_height": {"l0": l0, "l1": l1, "r0": r0, "r1": r1}, "same_width": {"t0": t0, "t1": t1, "b0": b0, "b1": b1}}
        self.subtables = subtables
        self.free_blocks = {"lable_blocks":free_labels,"data_blocks":free_data}
        self.expected_size = expected_size
        self.expected_position = expected_position


    def is_enclosed(self):
        #checks whether there is a same_height and same_width label block
        return any(value is not None for value in self.label_blocks["same_height"].values()) and any(value is not None for value in self.label_blocks["same_width"].values())


    def is_prime(self):
        #checks if the size of the data block is prime, returns None, Horizontal, or Vertical
        for dimension in [0,1]:
            dim = self.data_block.size[dimension]
            if dim < 2:
                continue
            for divisor in range(2, int(dim ** 0.5) + 1):
                if dim % divisor == 0:
                    continue
            return dimension
        return None


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
                    block.get_relative_position(origin=self.expected_position)
        for table in self.subtables:
            table.get_relative_position(origin=self.expected_position)
            
    def to_json(self):
        data_block_json = self.data_block.to_json() if self.data_block else None

        label_blocks_json = {
            outer_key: {inner_key: inner_value.to_json() if inner_value else None 
                        for inner_key, inner_value in outer_value.items()} 
            for outer_key, outer_value in self.label_blocks.items()
        }

        subtables_json = [subtable.to_json() for subtable in self.subtables]

        free_label_blocks_json = [block.to_json() for block in self.free_blocks["lable_blocks"]]
        free_data_blocks_json = [block.to_json() for block in self.free_blocks["data_blocks"]]

        table_json = {
            "data_block": data_block_json,
            "label_blocks": label_blocks_json,
            "subtables": subtables_json,
            "free_blocks": {"LABEL": free_label_blocks_json, "DATA": free_data_blocks_json},
        }

        return table_json
"""
class gen_tree:
    def __init__(self, json_data):
        self.data = json.loads(json_data)
        self.previous_data = None
        self.csv = self.build_csv()

    def build_csv(self):
        csv_data = []
        for sheet_name, sheet_data in self.data.items():
            csv_data.append([sheet_name, sheet_data])
        return csv_data

    def store(self):
        self.previous_data = self.data

    def cleaned_hierarchy_output(self):
        pass

    def to_json(self):
        return json.dumps(self.data)

    def get_incomplete_tables(self):
        pass

    def get_prime_width_tables(self):
        pass
"""



class eff_block:
    def __init__(self, cells: list[cell], annotation_type=None):
        self.cells = cells
        if len(cells) < 1:
            raise ValueError(f"Invalid block size, need at least one cell")
        self.get_corners()
        self.csv_format()
    
    def get_corners(self):
        max_coord = [float('-inf'), float('-inf')]
        min_coord = [float('inf'), float('inf')]
        csv_rows = []
        if not self.annotation_type:
            first_cell = self.cells[0]
            self.annotation_type = first_cell.block_type
        for cell in self.cells:
            if not self.annotation_type == cell.block_type:
                raise ValueError(f"Inconsistent block type, expecting type {self.annotation_type}, found cell with {cell.block_type}")
            for direction in [0,1]:
                if cell.coord[direction] > max_coord[direction]:
                    max_coord[direction] = cell.coord[direction]
                if cell.coord[direction] < min_coord[direction]:
                    min_coord[direction] = cell.coord[direction]
            csv_row = [cell.coord[0], cell.coord[1], cell.value, cell.annotation]
            csv_rows.append(csv_row)
        
        csv_string = ''
        if len(csv_rows) > 0:
            csv_string = '\n'.join([','.join(map(str, row)) for row in csv_rows])
        
        self.csv_data = csv_string
        self.corners = tuple(tuple(min_coord),tuple(max_coord))
        self.size = [int(self.corners[1][0]) - int(self.corners[0][0]), int(self.corners[1][1]) - int(self.corners[0][1])]
