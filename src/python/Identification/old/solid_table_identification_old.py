import json

# Load the output data from file
input_file_path = "blocks_output.json"
with open(input_file_path, "r") as file:
    sheets_data = json.load(file)

# Function to check if two blocks are adjacent or have no blocks between them
def is_adjacent_or_no_blocks_between(block1, block2, all_blocks):
    # Check if the blocks are adjacent
    if block1["end_row"] + 1 == block2["start_row"]:
        return True
    
    # Check if there are no blocks between them
    for annotation, blocks in all_blocks.items():
        for other_block in blocks:
            if (other_block["start_row"] > block1["end_row"] and other_block["start_row"] < block2["start_row"]):
                return False
    
    return True

# Process each sheet in the input data
solid_tables = []
for sheet_data in sheets_data:
    sheet_number = sheet_data["sheet_number"]
    blocks = sheet_data["blocks"]

    # Go through LABEL blocks
    for label_block in blocks.get("LABEL", []):
        # Look for matching DATA blocks
        for data_block in blocks.get("DATA", []):
            # Check if size matches, directly aligned, and either adjacent or no blocks between
            """ if (len(label_block["cells"]) == len(data_block["cells"]) and
                label_block["start_column"] == data_block["start_column"] and
                is_adjacent_or_no_blocks_between(label_block, data_block, blocks)):"""
            """if (len(label_block["cells"]) == len(data_block["cells"]) and
                label_block["start_column"] == data_block["start_column"]):"""
            if (len(label_block["cells"]) == len(data_block["cells"])):
                
                # Create a solid table
                solid_table = {
                    "sheet_number": sheet_number,
                    "label_block": label_block,
                    "data_block": data_block
                }
                solid_tables.append(solid_table)

# Optionally, save the solid-tables to a new JSON file
output_file_path = "solid_tables.json"
with open(output_file_path, "w") as outfile:
    json.dump(solid_tables, outfile, indent=4)

# Display the solid-tables
for solid_table in solid_tables:
    sheet_number = solid_table["sheet_number"]
    label_block = solid_table["label_block"]
    data_block = solid_table["data_block"]
    print(f"Sheet {sheet_number} - Solid Table:")
    print(f"  LABEL block: row {label_block['start_row']} to {label_block['end_row']}, columns {label_block['start_column']} to {label_block['end_column']}")
    print(f"  DATA block: row {data_block['start_row']} to {data_block['end_row']}, columns {data_block['start_column']} to {data_block['end_column']}")
    print("\n")
