# Class to represent a block of cells in the grid
import re
import pandas as pd
class Cell:
    def __init__(self, location: tuple, value=" ", annotation=None) -> None:
        # Set the cell value and annotation (default is 'EMPTY')
        self.value = value
        self.annotation = annotation
        self.relative_position = (0,0)
        # Define block type based on annotation
        if self.annotation == "FORMULA":
            self.block_type = "DATA"
        else:
            self.block_type = self.annotation
        # Handle coordinates in different formats
        if isinstance(location, str):
            self.coord_string = location
            # If string matches the pattern of a tuple of integers, convert it to tuple
            if re.match(r"\(\s*\d+\s*,\s*\d+\s*\)", self.coord_string):
                self.coord = tuple(map(int, self.coord_string.replace(
                    "(", "").replace(")", "").split(', ')))
            else:
                self.coord_num()
        elif isinstance(location, tuple):
            self.coord = location
        else:
            raise ValueError(
                f"Invalid Cell coordinate: expected tuple or 'A1' format, got {location}")

    def __str__(self):
        # String representation of the cell in the desired format
        return f"[{self.block_type}] '{self.value}'"

    def check_df_ep(self, df):
        # Note: pandas DataFrames are indexed by [row, column] contrary to the usual [x, y] indexing
        df_value = df.iloc[self.coord[1], self.coord[0]]
        if df_value == self.value:
            return True
        elif pd.isnull(df_value) or str(df_value).isspace():
            return False
        else:
            return df_value

    def to_clean_json(self):
        return f"{self.coord}: [{self.block_type}] '{self.value}'"

    # Function to convert Excel-like coordinates (e.g., 'A1') to numeric coordinates
    def coord_num(self):
        match = re.match(r'([A-Z]+)(\d+)', self.coord_string)
        if not match:
            raise ValueError(
                f"Invalid Excel coordinate, expected 'A1' format, got {self.coord_string}")

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

        self.coord = (x, y)

    def get_size(self):
        return 1
    
    # Function to serialize the cell object into a JSON format
    def to_json(self):
        return {"coord": self.coord, "value": self.value, "annotation": self.annotation}

    # Class method to create a cell object from a JSON data
    def from_json(self, json_data, coord):
        if not coord:
            coord = json_data.get("coord")
        value = json_data.get("value")
        annotation = json_data.get("annotation")
        return Cell(coord, value, annotation)

    # Function to get the position of the block relative to an origin
    def get_relative_position(self, origin: tuple):
        # gets relative position of top left corner based on a given origin
        relative_position = []
        for dimension in [0, 1]:
            relative_position.append(
                self.coord[dimension] - origin[dimension])
        self.relative_position = tuple(relative_position)
        return self.relative_position
        