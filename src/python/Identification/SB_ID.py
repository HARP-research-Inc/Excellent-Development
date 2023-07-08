# Import necessary libraries
import json
import re
from collections import defaultdict
import sys


# Load the JSON data from file
file_path = "src/python/JSONs/annotated_output.json"
with open(file_path, "r") as file:
    sheets = json.load(file)


# Function to extract the number from the cell name
def extract_number(cell_name):
    return int(re.findall(r'\d+', cell_name)[0])


def extract_column(cell_name):
    # The regular expression '[A-Z]+' matches one or more uppercase letters.
    # This time we ignore any non-alphabetic character
    return re.search(r'[A-Z]+', re.sub(r'[^A-Z]', '', cell_name)).group()


# Function to generate blocks of cells with the same annotation
def generate_solid_blocks(sheet):
    blocks = defaultdict(list)

    current_annotation = None
    current_block = {}
    current_row = None
    block_start_row = None
    block_start_column = None
    previous_column = None

    annots = {
        'DATA': [
            'DATA',
            'FORMULA'],
        'FORMULA': [
            'DATA',
            'FORMULA'],
        'LABEL': ['LABEL'],
        'EMPTY': ['EMPTY']}

    for cell, info in sorted(
        sheet["Annotations"].items(), key=lambda x: (
            extract_number(
            x[0]), x[0])):
        row_number = extract_number(cell)
        column_letter = extract_column(cell)

        # Check if it's the first cell or the cell is non-sequential or the cell has a different annotation
        if current_row is None or row_number != current_row or (previous_column is not None and column_letter != chr(ord(previous_column) + 1)) or current_annotation not in annots[info["annotation"]]:
            # Save the current block if it's not empty and if it's not 'EMPTY'
            if current_block and current_annotation != 'EMPTY':
                blocks[annots[current_annotation][0]].append({
                    "start_row": block_start_row,
                    "end_row": current_row,
                    "start_column": block_start_column,
                    "end_column": extract_column(list(current_block.keys())[-1]),
                    "cells": current_block
                })
            # Start a new block
            current_block = {cell: info}
            current_annotation = annots[info["annotation"]][0]
            block_start_row = row_number
            block_start_column = column_letter
        elif current_annotation in annots[info["annotation"]]:
            current_block[cell] = info
        
        current_row = row_number
    
    # Update the previous_column after processing the cell
    previous_column = column_letter

    # Save the last block if it's not empty and if it's not 'EMPTY'
    if current_block and current_annotation != 'EMPTY':
        blocks[current_annotation].append({
            "start_row": block_start_row,
            "end_row": current_row,
            "start_column": block_start_column,
            "end_column": extract_column(list(current_block.keys())[-1]),
            "cells": current_block
        })

    return blocks


def merge_blocks(blocks):
    merged_blocks = defaultdict(list)

    for annotation, block_list in blocks.items():
        merged_block = None

        for block in sorted(
            block_list,
            key=lambda x: (
                x["start_row"],
                x["start_column"])):
            if merged_block is None or block["start_row"] != merged_block["end_row"] or (
                    block["start_column"], block["end_column"]) != (
                    merged_block["start_column"], merged_block["end_column"]):
                if merged_block is not None:
                    merged_blocks[annotation].append(merged_block)
                merged_block = block.copy()
            else:
                merged_block["end_row"] = block["end_row"]
                merged_block["cells"].update(block["cells"])

        if merged_block is not None:
            merged_blocks[annotation].append(merged_block)

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
