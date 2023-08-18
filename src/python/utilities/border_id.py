 #? Title: border_id.py
 # Author: Harper Chisari

#? Contents:
#   CLASS - Border_Interaction_and_Identification: Holder for border_id method
#       #!LAST TESTED: 8/17/23
#       METHOD - __init__: Initializes a Border_Interaction_and_Identification object with border structures, base structures, combined structures, t, l, r, b, size constrained, and size flexible
#       METHOD - border_id: Identifies and interacts with border structures
#       METHOD - initialize_structures: Initializes the border, base, and combined structures
#       METHOD - find_valid_borders: Finds the valid borders for a given base structure
#       METHOD - process_base_structures: Processes the base structures by combining them with border structures
#       METHOD - process_data_structure: Specific logic for processing data structures 
#       METHOD - process_label_structure: Specific logic for processing label structures 
#       METHOD - process_table_structure: Specific logic for processing table structures 
#       METHOD - finalize_structures: Finalizes structures by updatating the appropriate lists

#? Version History:
# Version History:
#   Harper: 8/17/23 - V1.1 - refactored method for modularity
#   Harper: 8/17/23 - V1.0 - moved over from sheet_transformer.py for clarity

import sys

if 'pytest' in sys.modules:
    from src.python.utilities.relative_location_processor import RLP as rlp
    from src.python.utilities.gen_tree_helper import Gen_Tree_Helper as gth
    from src.python.structures.table import Table as tbl
    from src.python.structures.block import Block as blk
else:
    from utilities.relative_location_processor import RLP as rlp
    from utilities.gen_tree_helper import Gen_Tree_Helper as gth
    from structures.table import Table as tbl
    from structures.block import Block as blk

class Border_Interaction_and_Identification:
    def __init__(self, border_structures, base_structures, combined_structures, t=None, l=None, r=None, b=None, size_constrained=(True, True), size_flexible=(False, False)):
        self.border_structures = border_structures
        self.base_structures = base_structures
        self.combined_structures = combined_structures
        self.t = t
        self.l = l
        self.r = r
        self.b = b
        self.size_constrained = size_constrained
        self.size_flexible = size_flexible
        self.keys = ['l0', 'l1', 'r0', 'r1', 't0', 't1', 'b0', 'b1']

    # Identify and interact with border structures
    def border_id(self):
        self.initialize_structures()
        self.process_base_structures()
        self.finalize_structures()

    # Initialize the border, base, and combined structures
    def initialize_structures(self):
        self.unused_border_structures = {structure.expected_position: structure for structure in self.border_structures}
        self.unused_base_structures = {structure.expected_position: structure for structure in self.base_structures}
        self.new_combined_structures = {}

    # Find valid borders for a given base structure
    def find_valid_borders(self, base_structure) -> dict:
        valid_borders = {
            'same_height': {'l': {}, 'r': {}},
            'same_width': {'t': {}, 'b': {}}
        }
        # Check for matching border structures by comparing border eps
        for dimension, directions in rlp(structure=base_structure, t=self.t, l=self.l, r=self.r, b=self.b).border_eps.items():
            for direction, border_eps in directions.items():
                for border_ep in border_eps:
                    # retreived valid border structure if it exists
                    border_structure = self.unused_border_structures.get(border_ep)
                    if border_structure:
                        gth.debug_print(f"Border structure {border_ep} found")
                        # check if border structure is the same size as the base structure in the opposite dimension
                        same_size = border_structure.expected_size[0] == base_structure.expected_size[0] if dimension == 'same_width' else border_structure.expected_size[1] == base_structure.expected_size[1]

                        # check if border structure is within the base structure size in the opposite dimension
                        smaller_size = (
                            border_structure.corners[0][0] >= base_structure.corners[0][0]) and (
                            border_structure.corners[1][0] <= base_structure.corners[1][0]) if dimension == 'same_width' else (
                            border_structure.corners[0][1] >= base_structure.corners[0][1]) and (
                            border_structure.corners[1][1] <= base_structure.corners[1][1])

                        # check if border structure is size dependent in given dimension
                        size_dependent = self.size_constrained[0] if dimension == 'same_width' else self.size_constrained[1]
                        gth.debug_print(f"Border structure {border_ep} size dependent: {size_dependent}, same size: {same_size}")

                        # check if border structure is size flexible in given dimension
                        size_flex = self.size_flexible[0] if dimension == 'same_width' else self.size_flexible[1]
                        gth.debug_print(f"Border structure {border_ep} size flex: {size_flex}, smaller size: {smaller_size}")

                        if not size_dependent or same_size or (size_flex and smaller_size):
                            valid_borders[dimension][direction][border_ep] = border_structure
        return valid_borders

    # Process base structures by combining them with border structures and poping from dictionaries
    def process_base_structures(self):
        for base_structure in {structure.expected_position: structure for structure in self.base_structures}.values():
            table = tbl()
            valid_borders = self.find_valid_borders(base_structure)
            gth.debug_print(f"Base structure {base_structure.expected_position} border eps: {valid_borders}")

            border_check_order = [valid_borders['same_height']['l'],
                                 valid_borders['same_width']['t'],
                                 valid_borders['same_height']['r'],
                                 valid_borders['same_width']['b']]
            
            if isinstance(base_structure, blk):
                if base_structure.annotation_type == "LABEL":
                    border_check_order = reversed([valid_borders['same_height']['l'],
                                    valid_borders['same_width']['t'],
                                    valid_borders['same_height']['r'],
                                    valid_borders['same_width']['b']])
            
            # Process used base structures by creating tables and adding relevant blocks and subtables in order of left, top, right, bottom
            for dimension in border_check_order:
                for border_ep, border_structure in dimension.items():
                    if isinstance(base_structure, tbl):
                        self.process_table_structure(dimension, base_structure, base_structure, table)
                    elif base_structure.annotation_type == "DATA":
                        self.process_data_structure(dimension, base_structure, border_structure, table)
                    elif base_structure.annotation_type == "LABEL":
                        self.process_label_structure(dimension, base_structure, border_structure, table)

                    # Add the new combined structure to the dictionary
                    self.new_combined_structures[base_structure.expected_position] = table

                    # Remove used border structure from the unused dictionary
                    self.unused_border_structures.pop(border_ep)

                    # Remove used base structure from the unused dictionary
                    self.unused_base_structures.pop(base_structure.expected_position)

    # Reused logic for processing label block borders
    def label_border_process(self, dimension, base_structure, border_structure, table):
        #Iterate through label block locations
        for key in self.keys:
                # if key starts with with l or r, then it is a left or right label block with same height
                direction = 'same_height' if key[0] in ['l', 'r'] else 'same_width'

                # if ep not in border eps:
                if base_structure.border_eps[direction][key] != border_structure.expected_position:
                    # check if ep has a shared location corresponding to same location in base structure border eps
                    base_border_ep = base_structure.border_eps[direction][key]
                    shared_location_dimesnion = base_border_ep[1] == border_structure.expected_position[1] if direction == 'same_width' else base_border_ep[0] == border_structure.expected_position[0]

                    if shared_location_dimesnion:
                        # if so, check if there is a label block in the border eps at the spot where it would go:
                        if table.label_blocks[direction][key]:
                            # if true, combine label blocks into a bigger label block with cells of both
                            table.label_blocks[direction][key].cells.extend(border_structure.cells)

                        # else, add the label block from the border structure to the table in the spot where it would go
                        else:
                            table.label_blocks[direction][key] = border_structure

                    elif isinstance(base_structure, tbl):
                        table.free_blocks["label_blocks"].append(border_structure)

                # else, add the label block from the border structure to the table in the spot where it would go
                else:
                    table.label_blocks[direction][key] = dimension.get(base_structure.border_eps[direction][key])

    # Specific logic for processing data structures
    def process_data_structure(self, dimension, base_structure, border_structure, table):
        # If there's no data block, add the base structure as the data block, else extend the data block with the base structure
        if table.data_block:
            table.data_block.cells.extend(base_structure.cells)
        else:
            table.data_block = base_structure

        # Skip tables
        if isinstance(border_structure, tbl):
            return
        
        # If the border structure is a label block, add it as a label block border
        if border_structure.annotation_type == "LABEL":
            self.label_border_process(dimension, base_structure, border_structure, table)

        # If the border structure is a data block, extend the data block with the border data block
        elif border_structure.annotation_type == "DATA":
            table.data_block.cells.extend(border_structure.cells)

    # Specific logic for processing label structures
    def process_label_structure(self, dimension, base_structure, border_structure, table):
        # Skip table border structures
        if isinstance(border_structure, tbl):
            return

        # If the border structure is a label block, combine and add as free block
        if border_structure.annotation_type == "LABEL":
            # Extend border structure to the table's free blocks
            # If the base label block isnt in the table's free blocks, add it with the extension.
            # If it is, remove it first, then add with extension
            table.free_blocks["label_blocks"].append(base_structure).cells.extend(border_structure.cells
                ) if not (
                base_structure in table.free_blocks["label_blocks"]) else table.free_blocks["label_blocks"].remove(base_structure),
            table.free_blocks["label_blocks"].append(base_structure).cells.extend(border_structure.cells)

        # If the border structure is a data block, combine with table's current data block
        elif border_structure.annotation_type == "DATA":
            if table.data_block:
                table.data_block.cells.extend(border_structure.cells)
            else:
                table.data_block = border_structure

    # Specific logic for processing table structures
    def process_table_structure(self, dimension, base_structure, border_structure, table):
        table.subtables.append(base_structure)
        # Add the border structure according to its type
        if isinstance(border_structure, tbl):
            table.subtables.append(border_structure)

        elif border_structure.annotation_type == "DATA":
            table.free_blocks["data_blocks"].append(border_structure)

        elif border_structure.annotation_type == "LABEL":
            self.process_label_structure(dimension, base_structure, border_structure, table)

    # Finalize structures by updatating the appropriate lists
    def finalize_structures(self):
        self.border_structures[:] = list(self.unused_border_structures.values())
        self.base_structures[:] = list(self.unused_base_structures.values())
        self.combined_structures.extend(list(self.new_combined_structures.values()))
