 #? Title: gen_tree_helper.py
 # Author: Dana Solitaire

#? Contents:
#   CLASS - Gen_Tree_Helper:
#       #!LAST TESTED: 8/12/23
#       METHOD - debug_print: Conditional print method for debugging during testing
#       METHOD - create_grid: Creates a grid of True and False values from a list of cells
#       METHOD - insert_dataframe: A function which can combine dataframes with a relative origin
#       METHOD - get_border_eps: Gets the expected positions of adjacent blocks around the border of the block
#       METHOD - tuple_string_to_tuple: Converts a string representation of a tuple into a tuple of integers
#       METHOD - build_csv: Builds a CSV string from a list of cells, considering an optional origin point
#       METHOD - cut_csv_into_chunks: Converts a CSV string into a list of cells
#       METHOD - chunk_csv: Converts a CSV string into a list of cells
#       METHOD - join_or_concat_with_proper_alignment: Joins or concatenates two lists of lists of cells

#? Version History:
#   Harper: 8/17/23 - V1.3 added RLP with generalized border_id method and modified get_border_eps to use RLP, seperated RLP and MAR to seperate files
#   Harper: 8/15/23 - V1.2 added MaxAreaRectangles and create_grid
#   Harper: 8/12/23 - V1.1 added insert_dataframe, renamed to utilities.py, added titleblock
#   Dana: 8/1/23 - V1.0: added Gen_Tree_Helper


import sys
import csv

import pandas as pd
import numpy as np

from pandas import DataFrame
from io import StringIO
from itertools import zip_longest

if 'pytest' in sys.modules:
    from src.python.utilities.relative_location_processor import RLP as rlp
else:
    from utilities.relative_location_processor import RLP as rlp


# Class to help with general tree functions
class Gen_Tree_Helper:
    # Debug print method that only prints if pytest module is imported
    def debug_print(*args, **kwargs):
        if 'pytest' in sys.modules:
            print(*args, **kwargs)

    # Function to create a grid of True and False values from a list of cells
    def create_grid(cells):
        # Determine the size of the grid based on the cells
        max_x = max(cell.coord[0] for cell in cells)
        max_y = max(cell.coord[1] for cell in cells)
        grid = np.zeros((max_y + 1, max_x + 1), dtype=bool)

        # Populate the grid with True values for cells
        for cell in cells:
            grid[cell.coord[1], cell.coord[0]] = True

        return grid

    # Function to join or concatenate two lists of lists of cells
    def insert_dataframe(base_df: DataFrame, source_df: DataFrame, relative_origin: tuple = (1, 1)):
        if (relative_origin[0] < 1) or (relative_origin[1] < 1):
            raise ValueError(
                f'Relative origin is less than 1! Got RO of {relative_origin[0]}, {relative_origin[1]}')
        # Convert 1-based relative origin to 0-based
        row_origin, col_origin = relative_origin[1] - 1, relative_origin[0] - 1

        # Calculate the new shape required for the base DataFrame
        new_rows = max(base_df.shape[0], row_origin + source_df.shape[0])
        new_cols = max(base_df.shape[1], col_origin + source_df.shape[1])

        # Expand base DataFrame if needed
        if new_rows > base_df.shape[0]:
            base_df = base_df.append(pd.DataFrame(
                [[" "] * base_df.shape[1]] * (new_rows - base_df.shape[0])), ignore_index=True)
        if new_cols > base_df.shape[1]:
            for col in range(base_df.shape[1], new_cols):
                base_df[col] = [" "] * base_df.shape[0]

        # Copy values from source DataFrame to base DataFrame
        for row in range(source_df.shape[0]):
            for col in range(source_df.shape[1]):
                base_row = row + row_origin
                base_col = col + col_origin
                base_df.iat[base_row, base_col] = source_df.iat[row, col]
        # print(base_df)
        # print(f"EP: {relative_origin}")
        return base_df

    # Function to get the expected positions of adjacent blocks around the border of the block
    def get_border_eps(self):
        border_eps = rlp(structure=self).border_eps
        #print(f"{self.annotation_type} Block {self.expected_position} border_eps: {border_eps}")
        self.border_eps = {
            'same_height': {
                "l0": border_eps['same_height']['l'][0],
                "l1": border_eps['same_height']['l'][1],
                "r0": border_eps['same_height']['r'][0],
                "r1": border_eps['same_height']['r'][1]
            },
            "same_width": {
                "t0": border_eps['same_width']['t'][0],
                "t1": border_eps['same_width']['t'][1],
                "b0": border_eps['same_width']['b'][0],
                "b1": border_eps['same_width']['b'][1]
            },
        }
        return self.border_eps

    # Method to convert a tuple represented as a string into an actual tuple of integers
    def tuple_string_to_tuple(tuple_string: str) -> tuple[int, int]:
        assert isinstance(
            tuple_string, str), f"not a tuple string: {tuple_string}"
        return tuple(map(int, tuple_string.replace("(", "").replace(")", "").split(', ')))

    # Method to build a CSV from a list of cells and an optional origin
    def build_csv(cells, origin=(1, 1)):
        # Check if the origin is valid
        if any(cell.coord[i] < origin[i] for i in range(2) for cell in cells):
            raise ValueError("Origin is out of cells' range")

        # Check if cells are provided
        if len(cells) < 1:
            raise ValueError("No Cells!")

        # Determine the maximum number of rows and columns required
        max_rows = max(cell.coord[1] for cell in cells)
        max_cols = max(cell.coord[0] for cell in cells)

        # Initialize an empty grid starting at the origin
        grid = [["' '" for _ in range(origin[1]-1, max_cols)]
                for _ in range(origin[0]-1, max_rows)]

        # Fill the grid with the cell values
        for cell in cells:
            row = cell.coord[1] - origin[1]
            col = cell.coord[0] - origin[0]
            grid[row][col] = str(cell)

        # Convert the grid into rows of strings
        string_rows = []
        for row in grid:
            string_rows.append(', '.join(row))

        # Return the CSV as a string
        return '\n'.join(string_rows)

    # Method to convert a CSV string into a list of cells
    def cut_csv_into_chunks(csv_data, chunk_size, context_size):
        reader = csv.reader(StringIO(csv_data))
        data = list(reader)
        max_row_length = max(len(row) for row in data)
        data = [
            [
                ((col_idx, row_idx), cell) if cell != '' else (
                    (col_idx, row_idx), ' ')
                for col_idx, cell in enumerate(row + [' '] * (max_row_length - len(row)))
            ]
            for row_idx, row in enumerate(data)
        ]
        num_rows = len(data)
        num_cols = max_row_length
        num_row_chunks = -(-num_rows // chunk_size)  # Ceiling division
        num_col_chunks = -(-num_cols // chunk_size)  # Ceiling division
        chunked_rows = [
            [
                {
                    'chunk': [
                        row[start_col:end_col]
                        for row in data[start_row:end_row]
                    ],
                    'row_context': [
                        row[start_col:end_col]
                        for row in data[max(start_row - context_size, 0):start_row]
                    ] if i > 0 else [],
                    'col_context': [
                        row[max(start_col - context_size, 0):start_col]
                        for row in data[start_row:end_row]
                    ] if j > 0 else []
                }
                for j in range(num_col_chunks)
                for start_col, end_col in [
                    (j * chunk_size, min((j + 1) * chunk_size, num_cols))
                ]
                for start_row, end_row in [
                    (i * chunk_size, min((i + 1) * chunk_size, num_rows))
                ]
            ]
            for i in range(num_row_chunks)
        ]
        return chunked_rows

    # Method to convert a CSV string into a list of cells
    def chunk_csv(csv_data, chunk_size=5, context_size=2, name="Sheet 1"):
        all_sheets = {name:
                      Gen_Tree_Helper.cut_csv_into_chunks(
                          csv_data,
                          chunk_size,
                          context_size)}
        output_dict = {}
        for sheet_name, sheet in all_sheets.items():
            sheet_dict = {}
            for row_num, row in enumerate(sheet):
                row_dict = {}
                for chunk_num, chunk_info in enumerate(row):
                    combined = Gen_Tree_Helper.join_or_concat_with_proper_alignment(
                        chunk_info['row_context'], Gen_Tree_Helper.join_or_concat_with_proper_alignment(
                            chunk_info['chunk'], chunk_info['col_context'], 'join'), 'concat')
                    chunk_dict = {
                        "base_chunk": chunk_info['chunk'],
                        "contextualized_chunk": combined,
                    }
                    row_dict[f"Chunk {chunk_num+1}"] = chunk_dict
                sheet_dict[f"Row {row_num+1}"] = row_dict
            output_dict[sheet_name] = sheet_dict
        output_json = output_dict
        return output_json

    # Method to join or concatenate two lists of lists of cells
    def join_or_concat_with_proper_alignment(list1, list2, action='join'):
        if not list1:
            return list2
        if not list2:
            return list1
        len_diff = len(list2[0]) - len(list1[0])
        if len_diff > 0:
            list1 = [([(' ', ' ')] * len_diff) + row for row in list1]
        elif len_diff < 0:
            list2 = [([(' ', ' ')] * -len_diff) + row for row in list2]
        if action == 'join':
            return [b +
                    a for a, b in zip_longest(list1, list2, fillvalue=[('', ' ')] *
                                              len(list1[0]))]
        elif action == 'concat':
            return list1 + list2
