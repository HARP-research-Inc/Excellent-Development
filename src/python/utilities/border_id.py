 #? Title: border_id.py
 # Author: Harper Chisari

#? Contents:
#   CLASS - Border_Interaction_and_Identification: Holder for border_id method
#       #!LAST TESTED: 8/17/23
#       METHOD - border_id: Function to retrieve various border structures around a given block
#

#? Version History:
# Version History:
#   Harper: 8/17/23 - V1.0 - moved over from sheet_transformer.py for clarity

import sys

if 'pytest' in sys.modules:
    from src.python.utilities.relative_location_processor import RLP as rlp
    from src.python.structures.table import Table as tbl
else:
    from utilities.relative_location_processor import RLP as rlp
    from structures.table import Table as tbl

class Border_Interaction_and_Identification:
    #Function to retrieve various border structures around a given block
    def border_id(border_structures, base_structures, combined_structures, t=None, l=None, r=None, b=None, size_constrained=(False, False), size_flexible=(False, False)):
        # Initialize dictionaries to hold unused border structures, unused base structures, and new combined structures
        unused_border_structures = {structure.expected_position: structure for structure in border_structures}
        unused_base_structures = {structure.expected_position: structure for structure in base_structures}
        new_combined_structures = {}
        # Iterate over base structures to process them
        for base_ep, base_structure in {structure.expected_position: structure for structure in base_structures}.items():
            # Create an empty dict for Relative Location Processor (RLP) to hold border locations related to the current base structure
            valid_borders = {
            'same_height':
                {'l': {},
                    'r': {}},
            'same_width':
                {'t': {},
                    'b': {}}}

            # Check for matching border structures by comparing border eps
            for dimension, directions in rlp(structure=base_structure, t=t, l=l, r=r, b=b).border_eps.items():
                for direction, border_eps in directions.items():
                    for border_ep in border_eps:
                        # retreived valid border structure if it exists
                        border_structure = unused_border_structures.get(border_ep)
                        if border_structure:
                            print(f"Border structure {border_ep} found")
                            # check if border structure is the same size as the base structure in the opposite dimension
                            same_size = border_structure.expected_size[0] == base_structure.expected_size[0] if dimension == 'same_width' else border_structure.expected_size[1] == base_structure.expected_size[1]

                            # check if border structure is within the base structure size in the opposite dimension
                            smaller_size = (
                                border_structure.corners[0][0] >= base_structure.corners[0][0]) and (
                                border_structure.corners[1][0] <= base_structure.corners[1][0]) if dimension == 'same_width' else (
                                border_structure.corners[0][1] >= base_structure.corners[0][1]) and (
                                border_structure.corners[1][1] <= base_structure.corners[1][1])

                            # check if border structure is size dependent in given dimension
                            size_dependent = size_constrained[0] if dimension == 'same_width' else size_constrained[1]
                            print(f"Border structure {border_ep} size dependent: {size_dependent}, same size: {same_size}")

                            # check if border structure is size flexible in given dimension
                            size_flex = size_flexible[0] if dimension == 'same_width' else size_flexible[1]
                            print(f"Border structure {border_ep} size flex: {size_flex}, smaller size: {smaller_size}")

                            if not size_dependent or same_size or (size_flex and smaller_size):
                                valid_borders[dimension][direction][border_ep] = border_structure

            print(f"Base structure {base_ep} border eps: {valid_borders}")
            # Process used base structures by creating tables and adding relevant blocks and subtables in order of left, top, right, bottom
            for dimension in [valid_borders['same_height']['l'],
                                valid_borders['same_width']['t'],
                                valid_borders['same_height']['r'],
                                valid_borders['same_width']['b']]:

                for border_ep, border_structure in dimension.items():
                    table = tbl()  # Create a new table structure to hold the combined structure

                    # If the base structure is a data block, add it as the data block of the table
                    if base_structure.annotation_type == "DATA":
                        if table.data_block:
                            table.data_block.cells.extend(base_structure.cells)
                        else:
                            table.data_block = base_structure

                        # If the border structure is a label block, add it as a label block border
                        if border_structure.annotation_type == "LABEL":
                            keys = ['l0', 'l1', 'r0', 'r1', 't0', 't1', 'b0', 'b1']

                            #Iterate through label block locations
                            for key in keys:
                                # if key starts with with l or r, then it is a left or right label block with same height
                                direction = 'same_height' if key[0] in ['l', 'r'] else 'same_width'

                                # if ep not in border eps:
                                if base_structure.border_eps[direction][key] != border_ep:
                                    # check if ep has a shared location corresponding to same location in base structure border eps
                                    base_border_ep = base_structure.border_eps[direction][key]
                                    shared_location_dimesnion = base_border_ep[1] == border_ep[1] if direction == 'same_width' else base_border_ep[0] == border_ep[0]

                                    if shared_location_dimesnion:
                                        # if so, check if there is a label block in the border eps at the spot where it would go:
                                        if table.label_blocks[direction][key]:
                                            # if true, combine label blocks into a bigger label block with cells of both
                                            table.label_blocks[direction][key].cells.extend(border_structure.cells)

                                        # else, add the label block from the border structure to the table in the spot where it would go
                                        else:
                                            table.label_blocks[direction][key] = border_structure

                                # else, add the label block from the border structure to the table in the spot where it would go
                                else:
                                    table.label_blocks[direction][key] = dimension.get(base_structure.border_eps[direction][key])

                        # If the border structure is a data block, add it as a free block
                        elif border_structure.annotation_type == "DATA":
                            if table.data_block:
                                table.data_block.cells.extend(border_structure.cells)
                            else:
                                table.data_block = border_structure

                    # If the base structure is a label block
                    elif base_structure.annotation_type == "LABEL":
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

                    # If the base structure is a table, add as a subtable
                    elif isinstance(base_structure, tbl):
                        table.subtables.append(base_structure)
                        # Add the border structure according to its type
                        if border_structure.annotation_type == "LABEL":
                            keys = ['l0', 'l1', 'r0', 'r1', 't0', 't1', 'b0', 'b1']

                            #Iterate through label block locations
                            for key in keys:
                                # if key starts with with l or r, then it is a left or right label block with same height
                                direction = 'same_height' if key[0] in ['l', 'r'] else 'same_width'

                                # if ep not in border eps:
                                if base_structure.border_eps[direction][key] != border_ep:
                                    # check if ep has a shared location corresponding to same location in base structure border eps
                                    base_border_ep = base_structure.border_eps[direction][key]
                                    shared_location_dimesnion = base_border_ep[1] == border_ep[1] if direction == 'same_width' else base_border_ep[0] == border_ep[0]

                                    if shared_location_dimesnion:
                                        # if so, check if there is a label block in the border eps at the spot where it would go:
                                        if table.label_blocks[direction][key]:
                                            # if true, combine label blocks into a bigger label block with cells of both
                                            table.label_blocks[direction][key].cells.extend(border_structure.cells)

                                        # else, add the label block from the border structure to the table in the spot where it would go
                                        else:
                                            table.label_blocks[direction][key] = border_structure

                                    else:
                                        table.free_blocks["label_blocks"].append(border_structure)

                                # else, add the label block from the border structure to the table in the spot where it would go
                                else:
                                    table.label_blocks[direction][key] = dimension.get(base_structure.border_eps[direction][key])

                        elif border_structure.annotation_type == "DATA":
                            table.free_blocks["data_blocks"].append(border_structure)
                        elif isinstance(border_structure, tbl):
                            table.subtables.append(border_structure)

                    # Add the new combined structure to the dictionary
                    new_combined_structures[base_ep] = table

                    # Remove used border structure from the unused dictionary
                    unused_border_structures.pop(border_ep)

                    # Remove used base structure from the unused dictionary
                    unused_base_structures.pop(base_ep)

        # Update original list pointers to reflect the unused and new combined structures
        border_structures[:] = list(unused_border_structures.values())
        base_structures[:] = list(unused_base_structures.values())
        combined_structures[:] = list(new_combined_structures.values())
