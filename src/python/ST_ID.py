from structures.cell import Cell as cell
from structures.block import Block as block
from structures.table import Table as table
from structures.sheet import Sheet as sheet
from structures.gen_tree import Gen_Tree as gen_tree
from structures.utilities import Gen_Tree_Helper as gth
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
        #gth.debug_print(f"Leftover Labels: \n"+str({coord for coord in leftover_labels.keys()}))
        # Initialize a nested dictionary for storing position data
        pos_dict = {
            'same_height':{"l0": {}, "l1": {}, "r0": {}, "r1": {}}, 
            'same_width': {"t0": {}, "t1": {}, "b0": {}, "b1": {}}
        }

        # Iterate over data blocks in the Sheet
        for data_block in Sheet.free_data:
            # Get the border coordinates for each data block
            label_eps = data_block.get_border_eps()
            #gth.debug_print(f"Leftover Label Coords: \n"+str([coord for coord in leftover_labels.keys()]))
            # Create a hashmap mapping data coordinate tuples to data blocks
            data_coords[data_block.expected_position] = data_block

            # Check hashmap for free label blocks with the expected_position
            # If match is found, add the coordinate to the pos_dict 
            for dim in label_eps.keys():
                for ep, coord in label_eps[dim].items():
                    #print(f"Label ep: {ep}, coord: {coord}")
                    if coord in leftover_labels.keys():
                        #gth.debug_print("Label Match")
                        pos_dict[dim][ep][data_block.expected_position] = leftover_labels[coord]
                        #gth.debug_print(f"{ep}: {[{data: label.expected_position} for data, label in pos_dict[dim][ep].items()]}")
        ##gth.debug_print(f"pos_dict: \n"+str(pos_dict))

        # Iterate over possible positions
        for pos in (('same_height',"l0"), ('same_height',"l1"), ('same_width','t0'), ('same_width','t1'),
                    ('same_height',"r0"), ('same_height',"r1"), ('same_width','b0'), ('same_width','b1')):
            # Iterate over items in pos_dict corresponding to current position
            for data_coord, label in pos_dict[pos[0]][pos[1]].items():
                if label.expected_position in leftover_labels.keys():
                    #gth.debug_print(f"{label.expected_position} found unused")

                    # Create a new table if it doesn't already exist in the table dictionary
                    if not (data_coord in table_dict.keys()):
                        table_dict[data_coord] = table(data_block=data_coords[data_coord])
                        #gth.debug_print(f"Created new table for data at {data_coord}")

                    # Set the attribute of the table according to the current position
                    #gth.debug_print(f"Current position: {pos[1]}")
                    #gth.debug_print(f"Current position: {pos[1]} with value {getattr(table_dict[data_coord], 'label_blocks')[pos[0]][pos[1]]}")
                    table_dict[data_coord].label_blocks[pos[0]][pos[1]] = leftover_labels[label.expected_position]
                    #gth.debug_print(f"Current position: {pos[1]} with value {getattr(table_dict[data_coord], 'label_blocks')[pos[0]][pos[1]]}")
                    # Remove used labels from leftover_labels
                    leftover_labels.pop(label.expected_position)

        # Add processed sheet to sheet_dict
        sheet_dict[Sheet.name] = sheet(name=Sheet.name, tables=table_dict.values())

    # Return a new gen_tree object with processed sheets
    return gen_tree(sheets=sheet_dict)

def testfunc():
    # Prepare input data
    label_blocks = [
        block(annotation_type="LABEL", cells=[cell((2, 1), "Date", "LABEL"),
                                              cell((3, 1), "Time", "LABEL"),
                                              cell((4, 1), "Country", "LABEL")]),
        block(annotation_type="LABEL", cells=[cell((1, 2), "George Costanza", "LABEL"),
                                              cell((1, 3), "Bill Jeofry", "LABEL"),
                                              cell((1, 4), "Harper Giorgo", "LABEL")])
    ]
    data_blocks = [
        block(annotation_type = "DATA", cells=[
            cell((2, 2), "10/12/2023", "DATA"), cell((2, 3), "10:15", "DATA"), cell((2, 4), "USA", "DATA"), 
            cell((3, 2), "09/01/2002", "DATA"), cell((3, 3), "14:30", "DATA"), cell((3, 4), "UK", "DATA"), 
            cell((4, 2), "11/22/1963", "DATA"), cell((4, 3), "13:45", "DATA"), cell((4, 4), "Canada", "DATA")
        ])
    ]
    input_tree = gen_tree(sheets=[sheet(name="Sheet 1", free_labels=label_blocks, free_data=data_blocks)])
    print(input_tree.to_clean_json())

    # Call the function with the prepared input
    print(st_id(input_tree).to_clean_json())
    print(list(list(st_id(input_tree).sheets.values())[0].tables)[0].get_csv())
