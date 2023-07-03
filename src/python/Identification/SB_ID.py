# Import necessary libraries
import json
import re
from collections import defaultdict

# Load the JSON data from file
file_path = "JSONs/annotated_output.json"
with open(file_path, "r") as file:
    sheets = json.load(file)
    
# Function to extract the number from the cell name
def extract_number(cell_name):
    # The regular expression '\d+' matches one or more digits.
    # 're.search' returns a match object, and '.group()' returns the actual matched text.
    # In this case, it will return the numeric part of the cell name.
    return int(re.search(r'\d+', cell_name).group())

# Function to extract the column letter from the cell name
def extract_column(cell_name):
    # The regular expression '[A-Z]+' matches one or more uppercase letters.
    # Similar to the 'extract_number' function, this function returns the letter part of the cell name.
    return re.search(r'[A-Z]+', cell_name).group()

# Function to generate blocks of cells with the same annotation
def generate_solid_blocks(sheet):
    # Initialize a dictionary where keys are annotation types, and the values are lists of blocks of that type.
    blocks = defaultdict(list)
    
    # These variables will be used to keep track of the current block we are constructing.
    current_annotation = None
    current_block = {}
    current_row = None
    block_start_row = None
    block_start_column = None
    
    # Define a dictionary to group similar annotations together
    annots = {'DATA': ['DATA','FORMULA'], 'FORMULA': ['DATA','FORMULA'], 'LABEL': ['LABEL'], 'EMPTY': ['EMPTY']}

    # Loop over each cell. The cells are sorted by their row number.
    for cell, info in sorted(sheet["Annotations"].items(), key=lambda x: extract_number(x[0])):
        # Extract the row number and column letter from the cell name
        row_number = extract_number(cell)
        column_letter = extract_column(cell)

        # If it's the first cell we're processing, initialize our tracking variables.
        if current_row is None:
            current_row = row_number
            current_annotation = info["annotation"]
            block_start_row = row_number
            block_start_column = column_letter

        # If the cell's annotation matches the current block's annotation and the block's annotation is not 'EMPTY',
        # add the cell to the current block.
        if (current_annotation != 'EMPTY') and (current_annotation in annots[info["annotation"]]):
                current_block[cell] = info
        else:
            # If the cell's annotation doesn't match or the block's annotation is 'EMPTY',
            # save the current block if it's not empty,
            # and start a new block with this cell.
            if current_block and (current_annotation != 'EMPTY'):
                blocks[annots[current_annotation][0]].append({
                    "start_row": block_start_row,
                    "end_row": current_row,
                    "start_column": block_start_column,
                    "end_column": extract_column(list(current_block.keys())[-1]),
                    "cells": current_block
                })

            current_block = {cell: info}
            current_annotation = annots[info["annotation"]][0]
            block_start_row = row_number
            block_start_column = column_letter

        current_row = row_number

    # After looping over all cells, save the last block if it's not empty.
    if current_block and (current_annotation != 'EMPTY'):
        blocks[current_annotation].append({
            "start_row": block_start_row,
            "end_row": current_row,
            "start_column": block_start_column,
            "end_column": extract_column(list(current_block.keys())[-1]),
            "cells": current_block
        })

    # Return the blocks
    return blocks

# Function to merge blocks that are off by only a row and are the same length
def merge_blocks(blocks):
    # Initialize a dictionary for the merged blocks.
    merged_blocks = defaultdict(list)
    
    # Loop over each annotation type and its list of blocks
    for annotation, block_list in blocks.items():
        # The variable 'merged_block' keeps track of the current merged block we're working on.
        merged_block = None
        for block in block_list:
            # If it's the first block we're processing, or the current block doesn't start right after the merged block ends, 
            # or the two blocks have different numbers of cells,
            # then we add the current merged block to the list of merged blocks (if it's not None),
            # and we start a new merged block with the current block.
            if merged_block is None or \
               block["start_row"] != merged_block["end_row"] + 1 or \
               len(block["cells"]) != len(merged_block["cells"]):
                if merged_block is not None:
                    merged_blocks[annotation].append(merged_block)
                merged_block = block.copy()
            else:
                # If the current block starts right after the merged block ends, and the two blocks have the same number of cells,
                # then we merge these two blocks into one.
                # To merge the blocks, we update the 'end_row' and 'end_column' of the merged block,
                # and add all cells from the current block to the merged block.
                merged_block["end_row"] = block["end_row"]
                merged_block["end_column"] = block["end_column"]
                merged_block["cells"].update(block["cells"])

        # After looping over all blocks, save the last merged block (if it's not None).
        if merged_block is not None:
            merged_blocks[annotation].append(merged_block)

    # Return the merged blocks
    return merged_blocks


# Initialize a list to store the results.
results = []

# Loop over each sheet in the JSON data
for sheet in sheets:
    # Generate blocks for this sheet
    blocks = generate_solid_blocks(sheet)
    # Merge the generated blocks
    merged_blocks = merge_blocks(blocks)
    # Save the merged blocks in the results list
    results.append({
        "sheet_number": sheet['Sheet number'],
        "blocks": merged_blocks
    })

    # Display the merged blocks
    for annotation, block_list in merged_blocks.items():
        for i, block in enumerate(block_list):
            print(f"Sheet {sheet['Sheet number']}: {annotation} Block {i} from row {block['start_row']} to {block['end_row']}, columns {block['start_column']} to {block['end_column']}: {', '.join(block['cells'])}")

# Save the results to a JSON file
with open("blocks_output.json", "w") as outfile:
    json.dump(results, outfile, indent=4)
