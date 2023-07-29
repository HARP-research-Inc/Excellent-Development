import sys
if 'pytest' in sys.modules:
    from src.python.gen_tree_helper import Gen_Tree_Helper as gth
    from src.python.gen_tree import Gen_Tree as gt
    from src.python.cell import Cell as cell
else:
    from gen_tree_helper import Gen_Tree_Helper as gth
    from gen_tree import Gen_Tree as gt
    from cell import Cell as cell

class Block:
    def __init__(self, cells: list[cell] = [], annotation_type=None):
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

    def __str__(self):
        return str(self.to_json())

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
    
    #Function to get the expected positions of label blocks around the border of the block
    def get_border_eps(self):
        offsets = {
            'same_height': {
                "l0": (1, 0),
                "l1": (2, 0),
                # "r0": (1,0), temp until demo
                # "r1": (2,0)
            },
            "same_width": {
                "t0": (0, 1),
                "t1": (0, 2),
                # "b0": (0,1),
                # "b1": (0,2)
            }
        }
        self.border_eps = {
            'same_height': {},
            "same_width": {}}
        for directions, val in offsets.items():
            for label, coord in val.items():
                self.border_eps[directions][label] = tuple(
                    x - y for x, y in zip(self.expected_position, coord))
        return self.border_eps

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
            "size": "("+str(self.size[0]) + ', ' + str(self.size[1])+")",
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
        self.size = (int(self.corners[1][0]) - int(self.corners[0][0]) + 1,
                     int(self.corners[1][1]) - int(self.corners[0][1]) + 1)

    # Function to check if all cells in the block are of the same type as the block
    def check_consistancy(self):
        for cell in self.cells:
            if self.annotation_type == cell.block_type:
                pass
            else:
                raise ValueError(
                    f"Inconsistent block type, expecting type {self.annotation_type}, found cell with {cell.block_type}")

    # Function to get the annotation type of the block
    def get_annotation_type(self):
        first_cell = self.cells[0]
        self.annotation_type = first_cell.block_type

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
        for Cell in self.cells:
            Cell.get_relative_position(origin=self.expected_position) if not Cell.relative_position else None
        return self.relative_position

    # Class method to create a block object from a JSON data
    def from_json(cls, json_data):
        return cls(cells=[cell.from_json(cell_data, coord) for coord, cell_data in json_data["cells"].items()]) if json_data else None
