 #? Title: block.py
 # Author: Harper Chisari

#? Contents:
#   CLASS - Block: a block of cells with various attributes and methods to manipulate and represent the data.
#       #!LAST TESTED: 8/16/23
#       METHOD - __init__: Initializes a Block object with given cells and annotation type
#       METHOD - __str__: String representation of the Block object
#       METHOD - __repr__: Dictionary representation of the Block object
#       METHOD - check_df_ep: Checks if a dataframe has a compatible data structure
#       METHOD - to_dataframe: Returns a dataframe representation of the individual block
#       METHOD - get_size: Returns the size of the block
#       METHOD - to_json: Serializes the block object into a JSON format
#       METHOD - to_clean_json: Represents the Block as a list of cells
#       METHOD - get_corners: Finds the smallest and largest coordinates of cells in the block
#       METHOD - check_consistency: Checks if all cells in the block are of the same type
#       METHOD - get_annotation_type: Gets the annotation type of the block
#       METHOD - csv_format: Converts block data into CSV format
#       METHOD - get_relative_position: Gets the position of the block relative to an origin
#       METHOD - from_json: Creates a block object from JSON data
#       METHOD - is_solid: Checks if a block is solid

#? Version History:
#   Harper: 8/17/23 - V1.4 - added support for light blocks, and is_solid method

import sys
import pandas as pd


if 'pytest' in sys.modules:
    from src.python.structures.cell import Cell as cel
    from src.python.utilities.gen_tree_helper import Gen_Tree_Helper as gth

else:
    from structures.cell import Cell as cel
    from utilities.gen_tree_helper import Gen_Tree_Helper as gth

class Block:
    def __init__(self, cells: list[cel] = [], annotation_type=None):
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
        self.relative_position = self.expected_position
        gth.get_border_eps(self)

    # String Representation
    def __str__(self):
        return str(self.to_json())

    # Dictionary Representation
    def __repr__(self):
        return str(self.to_json())

    # Function to check if a dataframe has a compatible data structure
    def check_df_ep(self, df):
        mismatch_dict = {}
        for cell in self.cells:
            check_result = cell.check_df_ep(df)
            if check_result != True:
                mismatch_dict[cell.coord] = check_result
        if len(mismatch_dict) == len(self.cells):
            return False
        elif not mismatch_dict:
            return True
        return mismatch_dict

    # Function to return dataframe of individual block
    def to_dataframe(self):
        # Extract the top-left corner of the block as the relative origin
        relative_origin = self.expected_position

        # Create a dictionary with updated coordinates for each cell in the block
        cells_dict = {(cell.coord[1] - relative_origin[1], cell.coord[0] - relative_origin[0]): cell
                    for cell in self.cells}

        # Initialize an empty DataFrame with the appropriate size based on the corners
        cols, rows = self.expected_size
        df = pd.DataFrame([[" " for _ in range(cols)] for _ in range(rows)])

        # Populate the DataFrame using the cells_dict
        for (row, col), cell in cells_dict.items():
            df.iloc[row, col] = cell.value

        self.df = df
        return self.df

    # Function to get size of block
    def get_size(self):
        return self.expected_size

    # Function to serialize the block object into a JSON format
    def to_json(self):
        self.get_corners()
        # Represent cells as a dictionary, where keys are their coordinates
        cells_dict = {"("+str(cell.coord[0]) + ', ' + str(cell.coord[1])+")": {
            "value": cell.value, "annotation": cell.annotation} for cell in self.cells}
        block_json = {
            "start": "("+str(self.corners[0][0]) + ', ' + str(self.corners[0][1])+")",
            "end": "("+str(self.corners[1][0]) + ', ' + str(self.corners[1][1])+")",
            "cells": cells_dict,
            "size": "("+str(self.expected_size[0]) + ', ' + str(self.expected_size[1])+")",
        }
        return block_json

    # Represent Block only as list of cells within
    def to_clean_json(self):
        block_json = {
            "cells": [cell.to_clean_json() for cell in self.cells],
        }
        return block_json

    # Function to find the smallest and largest coordinates of cells in the block, effectively finding the corners
    def get_corners(self):
        max_coord = [float('-inf'), float('-inf')]
        min_coord = [float('inf'), float('inf')]
        for cell in self.cells:
            for direction in [0, 1]:
                if cell.coord[direction] > max_coord[direction]:
                    max_coord[direction] = cell.coord[direction]
                if cell.coord[direction] < min_coord[direction]:
                    min_coord[direction] = cell.coord[direction]
        self.corners = (tuple(min_coord), tuple(max_coord))
        self.expected_size = (int(self.corners[1][0]) - int(self.corners[0][0]) + 1,
                     int(self.corners[1][1]) - int(self.corners[0][1]) + 1)

    # Function to check if all cells in the block are of the same type as the block
    def check_consistancy(self):
        for cell in self.cells:
            if (self.annotation_type == cell.block_type) or (cell.block_type == 'EMPTY'):
                continue
            else:
                raise ValueError(
                    f"Inconsistent block type, expecting type {self.annotation_type}, found cell with {cell.block_type}")

    # Function to get the annotation type of the block
    def get_annotation_type(self):
        for cell in self.cells[0]:
            if cell.block_type != 'EMPTY':
                self.annotation_type = cell.block_type
                return
            else:
                continue
        raise ValueError("No annotation type found, empty block")

    # Function to convert block data into CSV format
    def csv_format(self):
        csv_rows = []
        for cell in self.cells:
            csv_row = [cell.coord[0], cell.coord[1],
                       cell.value, cell.annotation]
            csv_rows.append(csv_row)

        csv_string = ''
        if len(csv_rows) > 0:
            csv_string = '\n'.join([','.join(map(str, row))
                                   for row in csv_rows])

        self.csv_data = csv_string

    # Function to get the position of the block relative to an origin
    def get_relative_position(self, origin: tuple):
        # gets relative position of top left corner based on a given origin
        relative_position = []
        for dimension in [0, 1]:
            relative_position.append(
                self.expected_position[dimension] - origin[dimension])
        self.relative_position = tuple(relative_position)
        for cell in self.cells:
            cell.get_relative_position(origin=self.expected_position) if not cell.relative_position else None
        return self.relative_position

    # Class method to create a block object from a JSON data
    def from_json(json_data):
        return Block(cells=[cel.from_json(cel, cell_data, coord) for coord, cell_data in json_data["cells"].items()]) if json_data else None

    # Class method to check if a block is solid
    def is_solid(self):
        for cell in self.cells:
            if cell.annotation == 'EMPTY':
                return False
        return True
