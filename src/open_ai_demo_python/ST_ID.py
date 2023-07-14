from src.open_ai_demo_python.gen_tree import sheet, gen_tree, table

def st_id(tree: gen_tree):
    # Create a dictionary to store sheet information
    sheet_dict = {}

    # Iterate over each Sheet in the input tree
    for Sheet in tree.sheets.values():
        # Initialize a dictionary to store leftover labels
        leftover_labels = {}

        # Initialize a dictionary to store data coordinates
        data_coords = {}

        # Initialize a dictionary to store tables, using data coordinates as keys
        table_dict = {}

        # Create a hashmap mapping label coordinate tuples to free label blocks
        for label_block in Sheet.free_labels:
            leftover_labels[label_block.expected_position] = label_block

        # Initialize a nested dictionary for storing position data
        pos_dict = {
            'same_height':{"l0": {}, "l1": {}, "r0": {}, "r1": {}}, 
            'same_width': {"t0": {}, "t1": {}, "b0": {}, "b1": {}}
        }

        # Iterate over data blocks in the Sheet
        for data_block in Sheet.free_data:
            # Get the border coordinates for each data block
            label_eps = data_block.get_border_eps()

            # Create a hashmap mapping data coordinate tuples to data blocks
            data_coords[data_block.expected_position] = data_block

            # Check hashmap for free label blocks with the expected_position
            # If match is found, add the coordinate to the pos_dict 
            for dim in label_eps.keys():
                for ep, coord in label_eps[dim].items():
                    if coord in leftover_labels.keys():
                        pos_dict[dim][ep][data_block.expected_position] = leftover_labels[coord]

        # Iterate over possible positions
        for pos in (('same_height',"l0"), ('same_height',"l1"), ('same_width','t0'), ('same_width','t1'),
                    ('same_height',"r0"), ('same_height',"r1"), ('same_width','b0'), ('same_width','b1')):
            # Iterate over items in pos_dict corresponding to current position
            for data_coord, label_coord in pos_dict[pos[0]][pos[1]].items():
                if label_coord in leftover_labels.keys():
                    # Remove used labels from leftover_labels
                    leftover_labels.pop(label_coord)

                    # Create a new table if it doesn't already exist in the table dictionary
                    if not (data_coord in table_dict.keys()):
                        table_dict[data_coord] = table(data_block=data_coords[data_coord])

                    # Set the attribute of the table according to the current position
                    setattr(table_dict[data_coord], pos[1], leftover_labels[label_coord])

        # Add processed sheet to sheet_dict
        sheet_dict[Sheet.name] = sheet(name=Sheet.name, tables=table_dict.values())

    # Return a new gen_tree object with processed sheets
    return gen_tree(sheets=sheet_dict)
