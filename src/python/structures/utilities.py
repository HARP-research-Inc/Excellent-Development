import sys
import pandas as pd
from pandas import DataFrame
#Title: Utilities.py
#Author: Dana Solitaire

#Contents:
#   CLASS - Gen_Tree_Helper:
#       METHOD - debug_print: Conditional print method for debugging during testing
#       METHOD - tuple_string_to_tuple: Converts a string representation of a tuple into a tuple of integers
#       METHOD - build_csv: Builds a CSV string from a list of cells, considering an optional origin point
#       METHOD - insert_dataframe: A function which can combine dataframes with a relative origin

#Version History:
#   Harper: 8/12/23 - added insert_dataframe, renamed to utilities.py, added titleblock
#   Dana: 8/1/23 - V1.0: added Gen_Tree_Helper


class Gen_Tree_Helper:
    # Debug print method that only prints if pytest module is imported
    def debug_print(*args, **kwargs):
        if 'pytest' in sys.modules:
            print(*args, **kwargs)

    def insert_dataframe(base_df: DataFrame, source_df: DataFrame, relative_origin: tuple = (1,1)):
        if (relative_origin[0] < 1 ) or (relative_origin[1] < 1):
            raise ValueError(f'Relative origin is less than 1! Got RO of {relative_origin[0]}, {relative_origin[1]}')
        # Convert 1-based relative origin to 0-based
        row_origin, col_origin = relative_origin[1] - 1, relative_origin[0] - 1

        # Calculate the new shape required for the base DataFrame
        new_rows = max(base_df.shape[0], row_origin + source_df.shape[0])
        new_cols = max(base_df.shape[1], col_origin + source_df.shape[1])

        # Expand base DataFrame if needed
        if new_rows > base_df.shape[0]:
            base_df = base_df.append(pd.DataFrame([[" "] * base_df.shape[1]] * (new_rows - base_df.shape[0])), ignore_index=True)
        if new_cols > base_df.shape[1]:
            for col in range(base_df.shape[1], new_cols):
                base_df[col] = [" "] * base_df.shape[0]

        # Copy values from source DataFrame to base DataFrame
        for row in range(source_df.shape[0]):
            for col in range(source_df.shape[1]):
                base_row = row + row_origin
                base_col = col + col_origin
                base_df.iat[base_row, base_col] = source_df.iat[row, col]
        #print(base_df)
        #print(f"EP: {relative_origin}")
        return base_df

    # Method to convert a tuple represented as a string into an actual tuple of integers
    def tuple_string_to_tuple(tuple_string: str) -> tuple[int, int]:
        assert isinstance(tuple_string, str), f"not a tuple string: {tuple_string}"
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
