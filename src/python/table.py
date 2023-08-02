import pandas as pd
import sys
if 'pytest' in sys.modules:
    from src.python.gen_tree_helper import Gen_Tree_Helper as gth
    from src.python.block import Block as block
else:
    from gen_tree_helper import Gen_Tree_Helper as gth
    from block import Block as block

class Table:
    def __init__(self, expected_position=(1, 1), free_labels=[], free_data=[], subtables=[], l0=None, l1=None, r0=None, r1=None, t0=None, t1=None, b0=None, b1=None, data_block=None, json_data=None, pattern=None):
        assert isinstance(
            free_labels, list), f"expected a list, got f{free_labels}"
        self.data_block = data_block
        self.label_blocks = {"same_height": {"l0": l0, "l1": l1, "r0": r0,
                                             "r1": r1}, "same_width": {"t0": t0, "t1": t1, "b0": b0, "b1": b1}}
        self.subtables = subtables
        self.free_blocks = {
            "lable_blocks": free_labels, "data_blocks": free_data}
        self.expected_position = expected_position
        self.expected_size = (1,1)
        self.pattern = pattern
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
        for free_label in self.free_blocks["lable_blocks"]:
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

        # First we will create an empty DataFrame with sizes according to the table size
        df = pd.DataFrame('', index=range(
            self.expected_size[0]), columns=range(self.expected_size[1]))
        gth.debug_print(f"Data in DF in tble to_df: \n{self.expected_size}\n")
        self.get_child_rel_pos()
        # Initialize with the maximum possible size
        label_columns = [""] * self.expected_size[1]
        # Initialize with the maximum possible size
        label_indexes = [""] * self.expected_size[0]
        
        gth.debug_print(f"Label Columns: {label_columns}")
        gth.debug_print(f"Label Indexes: {label_indexes}")

        # We will then fill in the labels (if they exist) in the DataFrame
        for dim in (('same_width', "t0"), ('same_width', "t1"), ('same_height', "l0"), ('same_height', "l1")):
            if self.label_blocks[dim[0]][dim[1]]:
                label_block = self.label_blocks[dim[0]][dim[1]]
                if dim[0] == 'same_width':
                    # If it's the same width dimension, labels are placed on top of the DataFrame.
                    df.iloc[label_block.relative_position[0]:label_block.relative_position[0]+label_block.size[0],
                            label_block.relative_position[1]:label_block.relative_position[1]+label_block.size[1]] = [[Cell.value] for Cell in label_block.cells]
                    label_columns[label_block.relative_position[1]:label_block.relative_position[1] +
                                  label_block.size[1]] = [Cell.value for Cell in label_block.cells]
                else:
                    # If it's the same height dimension, labels are placed on the left side of the DataFrame.
                    df.iloc[label_block.relative_position[0]:label_block.relative_position[0]+label_block.size[0],
                            label_block.relative_position[1]:label_block.relative_position[1]+label_block.size[1]] = np.array([[Cell.value] for Cell in label_block.cells]).T
                    label_indexes[label_block.relative_position[0]:label_block.relative_position[0] +
                                  label_block.size[0]] = [Cell.value for Cell in label_block.cells]

        gth.debug_print(f"Labels in DF: {df}\n")
        df = df.transpose()
        # Finally we populate the DataFrame with data block values
        if self.data_block:
            cell_values = [Cell.value for Cell in self.data_block.cells]
            reshaped_cell_values = [cell_values[i:i+3]
                                    for i in range(0, len(cell_values), 3)]

            df.iloc[self.data_block.relative_position[0]:self.data_block.relative_position[0]+self.data_block.size[0],
                    self.data_block.relative_position[1]:self.data_block.relative_position[1]+self.data_block.size[1]] = reshaped_cell_values
        
        gth.debug_print(f"Data in DF in tble to_df: \n{df}\n")
        # Convert the DataFrame to have the correct labels as column names and indexes
        #Set the first row as the column names
        
        df.columns = df.iloc[0]

        # Remove the first row from the DataFrame
        df = df[1:]

        # Set the first column as the index
        df = df.set_index(df.columns[0])
        gth.debug_print(f"Indexed DF: \n{df}\n")
        df=df.transpose()

        return df

    def get_blocks(self):
        self.all_blocks = []
        if self.data_block:
            self.all_blocks.append(self.data_block)
        for dim in self.label_blocks["same_height"], self.label_blocks["same_width"]:
            for key, value in dim.items():
                if value is not None:
                    self.all_blocks.append(value)
        for block_list in [self.free_blocks["lable_blocks"], self.free_blocks["data_blocks"]]:
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
        #print(self.free_blocks)
        # If data_block is not None, get its size, otherwise, initialize total_size as [0, 0]
        total_size = list(self.data_block.size) if self.data_block else [0, 0]
        offsets = [[["same_height", "l0"], [1, 0]], [["same_height", "l1"], [2, 0]], [["same_height", "r0"], [1, 0]], [["same_height", "r1"], [
            2, 0]], [["same_width", "t0"], [0, 1]], [["same_width", "t1"], [0, 2]], [["same_width", "b0"], [0, 1]], [["same_width", "b1"], [0, 2]]]
        # Above offsets specify how the size of each label block contributes to the total size of the table

        for offset in offsets:
            block = self.label_blocks[offset[0][0]][offset[0][1]]
            if block:  # If the block exists
                for coord in [0, 1]:  # For each dimension
                    # Add the contribution of the block to the total size
                    total_size[coord] += offset[1][coord]
        self.expected_size = tuple(total_size)  # Set the expected size
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
                                  for block in self.free_blocks["lable_blocks"]]
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
        ) for block in self.free_blocks["lable_blocks"]]  # Convert the free label blocks to JSON
        free_data_blocks_clean_json = [block.to_clean_json(
        ) for block in self.free_blocks["data_blocks"]]  # Convert the free data blocks to JSON

        table_clean_json = {
            "data_block": data_block_clean_json,
            "label_blocks": label_blocks_clean_json,
            "subtables": subtables_clean_json,
            "free_blocks": free_label_blocks_clean_json + free_data_blocks_clean_json
        }  # Combine all the components into a JSON object

        return table_clean_json  # Return the JSON object

    def from_json(cls, json_data):
        # Reconstructs the table from a JSON object
        label_blocks_json = json_data.get("label_blocks", {})
        label_blocks = {
            "same_height": {
                "l0": block.from_json(label_blocks_json.get("same_height", {}).get("l0")),
                "l1": block.from_json(label_blocks_json.get("same_height", {}).get("l1")),
                "r0": block.from_json(label_blocks_json.get("same_height", {}).get("r0")),
                "r1": block.from_json(label_blocks_json.get("same_height", {}).get("r1"))
            },
            "same_width": {
                "t0": block.from_json(label_blocks_json.get("same_width", {}).get("t0")),
                "t1": block.from_json(label_blocks_json.get("same_width", {}).get("t1")),
                "b0": block.from_json(label_blocks_json.get("same_width", {}).get("b0")),
                "b1": block.from_json(label_blocks_json.get("same_width", {}).get("b1"))
            }
        }  # Above recreates the label blocks from JSON

        subtables = [cls.from_json(subtable_data) for subtable_data in json_data.get(
            "subtables", [])]  # Recreates the subtables from JSON

        free_blocks_json = json_data.get("free_blocks", {})
        free_labels = [block.from_json(block_data) for block_data in free_blocks_json.get(
            "LABEL", [])]  # Recreates the free label blocks from JSON
        free_data = [block.from_json(block_data) for block_data in free_blocks_json.get(
            "DATA", [])]  # Recreates the free data blocks from JSON

        # parse tuple
        expected_position = tuple(map(int, json_data.get(
            "start", "(0, 0)").strip("()").split(", ")))

        data_block = block.from_json(json_data.get("data_block")) if json_data.get(
            "data_block") else None  # Recreates the data block from JSON

        # Returns the recreated table
        return cls(expected_position, free_labels, free_data, subtables, *label_blocks["same_height"].values(), *label_blocks["same_width"].values(), data_block=data_block)
