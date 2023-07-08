import json

# Read the data from the file
def load_input_data(file_path):
    with open(file_path) as file:
        data = json.load(file)
    return data

# Save the data into a file
def save_output_data(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def is_smaller(label_block, data_block):
    # Check if both the width and height of label block are smaller than the data block
    return label_block['x_size'] <= data_block['x_size'] and label_block['y_size'] <= data_block['y_size']

def is_in_start_position(label_block, start_position):
    # Check if the start position of the label block is within the start position of the data block
    return label_block['pos']['start'] == start_position

def create_light_block(label_block, data_block, position_key):
    # Create a light block with similar structure to a regular block
    # The start and end positions correspond to the width or height of the data block
    light_block = {
        'pos': {
            'start': data_block['pos']['start'],
            'end': data_block['pos']['end']
        },
        'x_size': data_block['x_size'],
        'y_size': data_block['y_size'],
        'cells': label_block['cells'],
        'position': position_key
    }

    return light_block


def check_for_potential_light_blocks(data_block, free_labels):
    # Extract all the start positions (potential locations for light blocks)
    start_positions = data_block["start_pos"]
    light_blocks = []

    # Iterate over each start position
    for key, position in start_positions.items():
        # Check each free label
        for label in free_labels:
            # Check if label is smaller than data block and it's in one of the start positions
            if is_smaller(label, data_block) and is_in_start_position(label, position):
                # Create light block with same structure as regular block, but start and end position corresponds with the width or height of the data block
                light_block = create_light_block(label, data_block, key)
                light_blocks.append(light_block)

    return light_blocks


def label_light_block_search(solid_table, free_labels):
    light_blocks = check_for_potential_light_blocks(solid_table["data_blocks"], free_labels)
    solid_table["light_blocks"] = light_blocks
    return solid_table


# Search for pattern AB
def pattern_ab_search(free_label, free_data_blocks):
    potential_light_blocks = []
    
    # Iterate over each free data block
    for data_block in free_data_blocks:
        # Check for AB pattern
        if check_ab_pattern(free_label, data_block):
            potential_light_blocks.append(data_block)
    
    return potential_light_blocks

# Search for pattern BB
def pattern_bb_search(free_label, free_data_blocks):
    potential_light_blocks = []
    
    # Iterate over each free data block
    for data_block in free_data_blocks:
        # Check for BB pattern
        if check_bb_pattern(free_label, data_block):
            potential_light_blocks.append(data_block)
    
    return potential_light_blocks

# Search for pattern CB
def pattern_cb_search(free_label, free_data_blocks):
    potential_light_blocks = []
    
    # Iterate over each free data block
    for data_block in free_data_blocks:
        # Check for CB pattern
        if check_cb_pattern(free_label, data_block):
            potential_light_blocks.append(data_block)
    
    return potential_light_blocks

# Main function for identifying the light blocks
def identify_light_blocks(data):
    for sheet in data:
        for table in sheet["solid_tables"]:
            potential_light_blocks = check_for_potential_light_blocks(table["data"])
            if potential_light_blocks:
                table["light_blocks"] = potential_light_blocks

            if "LABEL" in sheet["free_solid_blocks"]:
                solid_table = label_light_block_search(table, sheet["free_solid_blocks"]["LABEL"])
            
            if "DATA" in sheet["free_solid_blocks"]:
                for free_label in solid_table["labels"]:
                    potential_light_blocks = pattern_ab_search(free_label, sheet["free_solid_blocks"]["DATA"])
                    potential_light_blocks += pattern_bb_search(free_label, sheet["free_solid_blocks"]["DATA"])
                    potential_light_blocks += pattern_cb_search(free_label, sheet["free_solid_blocks"]["DATA"])

                    if potential_light_blocks:
                        free_label["light_blocks"] = potential_light_blocks
    return data

def main():
    # Load the input data
    input_data = load_input_data('path_to_input_file.json')

    # Identify the light blocks
    output_data = identify_light_blocks(input_data)

    # Save the output data
    save_output_data(output_data, 'path_to_output_file.json')


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()
