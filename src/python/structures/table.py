import pandas as pd
import sys

# Title: table.py
# Author: Harper Chisari
# Description: Defines the Table class, representing a complex table structure comprising various blocks, labels, and subtables. Provides methods for DataFrame conversion, validation, JSON serialization, size calculation, and more.
# Contents:
#   CLASS - Table:
#       METHOD - __init__: Initializes a Table object with expected position, labels, data, subtables, and other attributes
#       METHOD - __str__: String representation of the Table object
#       METHOD - __repr__: String representation of the Table object
#       METHOD - check_df_ep: Checks if a DataFrame has a compatible data structure
#       METHOD - to_dataframe: Transposes and returns a DataFrame representation of the table
#       METHOD - get_blocks: Returns all blocks within the table
#       METHOD - get_csv: Builds a CSV representation of all cells in the table
#       METHOD - is_enclosed: Checks if the table is enclosed by labels
#       METHOD - is_prime: Checks if the size of the data block is prime
#       METHOD - get_relative_position: Gets the relative position of the table
#       METHOD - get_child_rel_pos: Calculates the relative position for each child block and subtable
#       METHOD - get_size: Computes and returns the size of the table
#       METHOD - to_json: Serializes the table object into a JSON format
#       METHOD - to_clean_json: Represents the Table in a cleaner JSON format
#       METHOD - from_json: Creates a Table object from JSON data

# Version History:
#   Harper: 8/12/23 - V1.3 - Added title block, redid to_dataframe, added get_corners

if 'pytest' in sys.modules:
    from src.python.structures.utilities import Gen_Tree_Helper as gth
    from src.python.structures.block import Block as blk
    from src.python.structures.cell import Cell as cel
else:
    from structures.utilities import Gen_Tree_Helper as gth
    from structures.block import Block as blk
    from structures.cell import Cell as cel


class Table:
    def __init__(self, free_labels=[], free_data=[], subtables=[], l0=None, l1=None, r0=None, r1=None, t0=None, t1=None, b0=None, b1=None, data_block: blk=None, json_data=None, pattern=None):
        assert isinstance(
            free_labels, list), f"expected a list, got f{free_labels}"
        self.data_block = data_block
        self.label_blocks = {"same_height": {"l0": l0, "l1": l1, "r0": r0,
                                             "r1": r1}, "same_width": {"t0": t0, "t1": t1, "b0": b0, "b1": b1}}
        self.subtables = subtables
        self.free_blocks = {
            "label_blocks": free_labels, "data_blocks": free_data}
        self.get_corners()
        self.pattern = pattern
        self.all_blocks = []
        # Get the size of the table after initializing all the attributes
        self.get_size()

    def __str__(self):
        return str(self.to_json())

    def __repr__(self):
        return str(self.to_json())
    
    def check_df_ep(self, df):
        # Create an empty dictionary to store mismatches for label blocks
        label_mismatch_dict = {}
        # Create an empty dictionary to store mismatches for free labels
        free_label_mismatch_dict = {}
        # Create an empty dictionary to store mismatches for subtables
        subtable_mismatch_dict = {}

        # Loop over each label block
        for dimension in ['same_height', 'same_width']:
            for label_position in self.label_blocks[dimension].keys():
                label_block = self.label_blocks[dimension][label_position]

                # Check if the block exists
                if label_block is not None:
                    # Use the block's check_df_ep method to check for mismatches
                    label_check_result = label_block.check_df_ep(df)

                    # If check_df_ep returns False, return False
                    if label_check_result == False:
                        return False
                    # If check_df_ep returns a dictionary (indicating mismatches),
                    # add it to the label_mismatch_dict
                    elif label_check_result != True:
                        label_mismatch_dict[label_position] = label_check_result

        # Loop over each free label
        for free_label in self.free_blocks["label_blocks"]:
            # Use the block's check_df_ep method to check for mismatches
            free_label_check_result = free_label.check_df_ep(df)

            # If check_df_ep returns False, return False
            if free_label_check_result == False:
                return False
            # If check_df_ep returns a dictionary (indicating mismatches),
            # add it to the free_label_mismatch_dict
            elif free_label_check_result != True:
                free_label_mismatch_dict[free_label] = free_label_check_result

        # Check if the data block exists
        if self.data_block is not None:
            # Use the data block's check_df_ep method to check for mismatches
            data_check_result = self.data_block.check_df_ep(df)

            # If check_df_ep returns True, return True
            if data_check_result == True:
                return True
            # If check_df_ep returns a dictionary (indicating mismatches),
            # update the corresponding cell values in the data block
            elif isinstance(data_check_result, dict):
                for coord, value in data_check_result.items():
                    # Find the cell with the mismatched coordinate
                    cell = next((cell for cell in self.data_block.cells if cell.coord == coord), None)
                    if cell is not None:
                        # Update the cell's value
                        cell.value = value

        # Check for mismatches in the free data blocks
        for free_data_block in self.free_data:
            free_data_check_result = free_data_block.check_df_ep(df)
            if isinstance(free_data_check_result, dict):
                for coord, value in free_data_check_result.items():
                    cell = next((cell for cell in free_data_block.cells if cell.coord == coord), None)
                    if cell is not None:
                        cell.value = value

        # Check for mismatches in the subtables
        for subtable in self.subtables:
            subtable_check_result = subtable.check_df_ep(df)
            if subtable_check_result != True:
                subtable_mismatch_dict[subtable] = subtable_check_result

        # Combine all mismatch dictionaries
        all_mismatches = {**label_mismatch_dict, **free_label_mismatch_dict, **subtable_mismatch_dict}

        # If there are any mismatches, return the dictionary of mismatches
        # If not, return True
        return all_mismatches if all_mismatches else True

    def to_dataframe(self):
        # Get DataFrames and expected positions (eps) of all free label blocks, free data blocks, label blocks, and the data block
        all_dfs = []
        for block_type in [self.free_blocks["label_blocks"], self.free_blocks["data_blocks"], self.label_blocks["same_height"].values(), self.label_blocks["same_width"].values()]:
            for block in block_type:
                if block:
                    all_dfs.append((block.to_dataframe(), block.expected_position))
        if self.data_block:
            all_dfs.append((self.data_block.to_dataframe(), self.data_block.expected_position))

        # Use gth.insert_dataframe to concatenate all DataFrames into a larger one
        df = pd.DataFrame()
        for dataframe, expected_position in all_dfs:
            new_ep = (expected_position[0] - (self.expected_position[0] - 1), expected_position[1] - (self.expected_position[1] - 1))
            gth.debug_print(f"  Table EP: {self.expected_position}, Block EP: {expected_position}")
            #gth.debug_print(self.free_blocks)
            #self.get_corners()
            #gth.debug_print(self)
            df = gth.insert_dataframe(df, dataframe, new_ep)

        # Return and assign the concatenated DataFrame to self.dataframe
        self.dataframe = df
        return df

    def get_corners(self) -> tuple:
        #label offset
        label_offset_x = -2 if self.label_blocks["same_height"]["l1"] else -1 if self.label_blocks["same_height"]["l0"] else 0
        label_offset_y = -2 if self.label_blocks["same_width"]["t1"] else -1 if self.label_blocks["same_width"]["t0"] else 0
        label_offset_x1 = 2 if self.label_blocks["same_height"]["r1"] else 1 if self.label_blocks["same_height"]["r0"] else 0
        label_offset_y1 = 2 if self.label_blocks["same_width"]["b1"] else 1 if self.label_blocks["same_width"]["b0"] else 0
        #initialize corners
        self.corners = []
        #take data block ep and offset table ep depending on labels used
        self.corners = [(self.data_block.expected_position[0] + label_offset_x, self.data_block.expected_position[1] + label_offset_y), (self.data_block.corners[1][0] + label_offset_x1, self.data_block.corners[1][1] + label_offset_y1)]
        #see if any free block is further out
        gth.debug_print(f"  Corners pre-fb check: {self.corners}")
        free_blocks = self.free_blocks["label_blocks"] + self.free_blocks["data_blocks"]
        max_corners = self.corners
        #check free block corners
        for block in free_blocks:
            gth.debug_print(f"      Block Corners: {block.corners}")
            max_corners[0] = (block.corners[0][0], max_corners[0][1]) if block.corners[0][0] < max_corners[0][0] else max_corners[0]
            max_corners[0] = (max_corners[0][0], block.corners[0][1]) if block.corners[0][1] < max_corners[0][1] else max_corners[0]
            max_corners[1] = (block.corners[1][0], max_corners[1][1]) if block.corners[1][0] > max_corners[1][0] else max_corners[1]
            max_corners[1] = (max_corners[1][0], block.corners[1][1]) if block.corners[1][1] > max_corners[1][1] else max_corners[1]

        for subtable in self.subtables:
            gth.debug_print(f"      Subtable Corners: {subtable.corners}")
            max_corners[0] = (subtable.corners[0][0], max_corners[0][1]) if subtable.corners[0][0] < max_corners[0][0] else max_corners[0]
            max_corners[0] = (max_corners[0][0], subtable.corners[0][1]) if subtable.corners[0][1] < max_corners[0][1] else max_corners[0]
            max_corners[1] = (subtable.corners[1][0], max_corners[1][1]) if subtable.corners[1][0] > max_corners[1][0] else max_corners[1]
            max_corners[1] = (max_corners[1][0], subtable.corners[1][1]) if subtable.corners[1][1] > max_corners[1][1] else max_corners[1]
        
        gth.debug_print(f"  Corners post- item check: {self.corners}")

        #update ep
        self.expected_position = self.corners[0]
        return self.expected_position

    def get_blocks(self) -> list:
        if self.data_block:
            self.all_blocks.append(self.data_block)
        for dim in self.label_blocks["same_height"], self.label_blocks["same_width"]:
            for key, value in dim.items():
                if value is not None:
                    self.all_blocks.append(value)
        for block_list in [self.free_blocks["label_blocks"], self.free_blocks["data_blocks"]]:
            self.all_blocks += block_list
        return self.all_blocks

    def get_csv(self):
        self.get_blocks()
        all_cells = []
        for Block in self.all_blocks:
            all_cells += Block.cells
        return (gth.build_csv(all_cells, self.expected_position))

    def is_enclosed(self):
        # Checks if the table is enclosed by labels from both height and width dimensions
        return any(value is not None for value in self.label_blocks["same_height"].values()) and any(value is not None for value in self.label_blocks["same_width"].values())

    def is_prime(self):
        # Checks if the size of the data block is prime, returns None if not, else returns the dimensions that are prime
        dims = []
        if self.data_block is None:
            return None  # If there is no data block, return None

        for dimension in [0, 1]:  # For each dimension of the data block
            dim = self.data_block.size[dimension]
            if dim < 2:  # If dimension is less than 2, it's not prime, so continue to next dimension
                continue
            # Check if the dimension is divisible by any number up to its square root
            for divisor in range(2, int(dim ** 0.5) + 1):
                if dim % divisor == 0:  # If it is, break the loop and move on to next dimension
                    break
            else:
                # If not, then the dimension is prime, so add it to the dims list
                dims.append(dimension)

        return dims if dims else None  # Return the prime dimensions if any, else return None

    def get_relative_position(self, origin: tuple):
        # Gets the relative position of the top left corner of the table based on a given origin
        relative_position = []
        for dimension in [0, 1]:  # For each dimension
            relative_position.append(
                self.expected_position[dimension] - origin[dimension])
        self.relative_position = tuple(relative_position)
        return self.relative_position  # Returns the relative position

    def get_child_rel_pos(self):
        # Calculate the relative position for each child block and subtable
        if self.data_block:  # If there is a data block
            self.data_block.get_relative_position(
                self.expected_position) if not self.data_block.relative_position else None  # Calculate its relative position
        for dim in ["same_height", "same_width"]:  # For each dimension
            # For each label block in the dimension
            for Block in self.label_blocks[dim].values():
                if Block:  # If the label block exists
                    # Calculate its relative position
                    Block.get_relative_position(origin=self.expected_position) if not Block.relative_position else None
        for Table in self.subtables:  # For each subtable
            # Calculate its relative position
            Table.get_relative_position(origin=self.expected_position) if not Table.relative_position else None

    def get_size(self):
        self.expected_size = (self.corners[1][0] - (self.corners[0][0]-1), self.corners[1][1] - (self.corners[0][1]-1))
        return self.expected_size

    def to_json(self):
        self.get_size()
        # Converts the table to a JSON format for easy saving and loading
        # Convert the data block to JSON if it exists
        data_block_json = self.data_block.to_json() if self.data_block else None

        label_blocks_json = {
            outer_key: {inner_key: inner_value if inner_value else None
                        for inner_key, inner_value in outer_value.items()}
            for outer_key, outer_value in self.label_blocks.items()
        }  # Convert the label blocks to JSON

        # Convert the subtables to JSON
        subtables_json = [subtable.to_json() for subtable in self.subtables]

        #print(self.free_blocks)
        # Convert the free label blocks to JSON
        free_label_blocks_json = [block.to_json()
                                  for block in self.free_blocks["label_blocks"]]
        # Convert the free data blocks to JSON
        free_data_blocks_json = [block.to_json()
                                 for block in self.free_blocks["data_blocks"]]

        table_json = {
            "data_block": data_block_json,
            "label_blocks": label_blocks_json,
            "subtables": subtables_json,
            "free_blocks": {"LABEL": free_label_blocks_json, "DATA": free_data_blocks_json},
            "size": "("+str(self.expected_size[0]) + ', ' + str(self.expected_size[1])+")",
            "start": "("+str(self.expected_position[0]) + ', ' + str(self.expected_position[1])+")",
        }  # Combine all the components into a JSON object

        return table_json  # Return the JSON object

    def to_clean_json(self):
        # Converts the table to a JSON format for easy saving and loading
        data_block_clean_json = self.data_block.to_clean_json(
        ) if self.data_block else None  # Convert the data block to JSON if it exists

        label_blocks_clean_json = {}
        for dim in ['same_height', 'same_width']:
            for Block in self.label_blocks[dim].values():
                if Block:
                    label_blocks_clean_json[Block.expected_position] = Block.to_clean_json(
                    )

        # Convert the subtables to JSON
        subtables_clean_json = [subtable.to_cean_json()
                                for subtable in self.subtables]

        #print(self.free_blocks)
        free_label_blocks_clean_json = [block.to_clean_json(
        ) for block in self.free_blocks["label_blocks"]]  # Convert the free label blocks to JSON
        free_data_blocks_clean_json = [block.to_clean_json(
        ) for block in self.free_blocks["data_blocks"]]  # Convert the free data blocks to JSON

        table_clean_json = {
            "data_block": data_block_clean_json,
            "label_blocks": label_blocks_clean_json,
            "subtables": subtables_clean_json,
            "free_blocks": free_label_blocks_clean_json + free_data_blocks_clean_json
        }  # Combine all the components into a JSON object

        return table_clean_json  # Return the JSON object

    def from_json(cls,json_data):
        # Reconstructs the table from a JSON object
        label_blocks_json = json_data.get("label_blocks", {})
        label_blocks = {
            "same_height": {
                "l0": block.from_json(json_data=label_blocks_json.get("same_height", {}).get("l0")),
                "l1": block.from_json(json_data=label_blocks_json.get("same_height", {}).get("l1")),
                "r0": block.from_json(json_data=label_blocks_json.get("same_height", {}).get("r0")),
                "r1": block.from_json(json_data=label_blocks_json.get("same_height", {}).get("r1"))
            },
            "same_width": {
                "t0": block.from_json(json_data=label_blocks_json.get("same_width", {}).get("t0")),
                "t1": block.from_json(json_data=label_blocks_json.get("same_width", {}).get("t1")),
                "b0": block.from_json(json_data=label_blocks_json.get("same_width", {}).get("b0")),
                "b1": block.from_json(json_data=label_blocks_json.get("same_width", {}).get("b1"))
            }
        }  # Above recreates the label blocks from JSON

        subtables = [cls.from_json(cell, subtable_data) for subtable_data in json_data.get(
            "subtables", [])]  # Recreates the subtables from JSON

        free_blocks_json = json_data.get("free_blocks", {})
        free_labels = [block.from_json(json_data=block_data) for block_data in free_blocks_json.get(
            "LABEL", [])]  # Recreates the free label blocks from JSON
        free_data = [block.from_json(json_data=block_data) for block_data in free_blocks_json.get(
            "DATA", [])]  # Recreates the free data blocks from JSON

        # parse tuple
        expected_position = tuple(map(int, json_data.get(
            "start", "(0, 0)").strip("()").split(", ")))

        data_block = block.from_json(json_data=json_data.get("data_block")) if json_data.get(
            "data_block") else None  # Recreates the data block from JSON

        # Returns the recreated table
        return Table(expected_position, free_labels, free_data, subtables, *label_blocks["same_height"].values(), *label_blocks["same_width"].values(), data_block=data_block)
