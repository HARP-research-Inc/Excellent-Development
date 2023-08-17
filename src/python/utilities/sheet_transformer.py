 #? Title: sheet_transformer.py
 # Author: Harper Chisari

#? Contents:
#   CLASS - Sheet_Transformer: Contains all algorithmic transformations and pre-processing for a sheet
#       #!LAST TESTED: 8/16/23
#       METHOD - get_annotated_chunk: Generates a CSV string of the chunk with the current cell highlighted and annotations included
#       METHOD - annotate_cells_ai: Uses OpenAI to predict if the cell is a label or data
#       METHOD - sb_id: Sorts cells by block_type, groups cells by block_type, creates blocks using MaxAreaRectangles and adds to sheet's blocks
#       METHOD - border_id: Identifies the border structures of a given base structure
#       METHOD - st_id: Identifies solid tables in the sheet
#
#   CLASSS - Constants: contains constants used in the sheet transformer
#       #!LAST TESTED: 8/16/23
#       VARIABLE - labeling_conversation: The conversation used to label cells with DaVinci 3.0 from openai

#? Version History:
# Version History:
#   Harper: 8/17/23 - V1.1 - added border_id and redid/completed title block
#   Harper: 8/16/23 - V1.0 - initial commit


import sys
import openai, os, csv
from io import StringIO


if 'pytest' in sys.modules:
    from src.python.utilities.gen_tree_helper import Gen_Tree_Helper as gth
    from src.python.utilities.max_area_rectangles import MaxAreaRectangles
    from src.python.utilities.relative_location_processor import RLP as rlp
    from src.python.structures.cell import Cell as cel
    from src.python.structures.block import Block as blk
    from src.python.structures.table import Table as tbl
else:
    from utilities.gen_tree_helper import Gen_Tree_Helper as gth
    from utilities.max_area_rectangles import MaxAreaRectangles
    from utilities.relative_location_processor import RLP as rlp
    from structures.cell import Cell as cel
    from structures.block import Block as blk
    from structures.table import Table as tbl


class Sheet_Transformer:
    def get_annotated_chunk(self, chunk, current_cell_id, annotated_output):
        # Generate a CSV string of the chunk with the current cell highlighted and
        # annotations included
        formatted_chunk = []
        for row in chunk:
            formatted_row = []
            for cell_id, cell_value in row:
                # Annotate formula cells
                if cell_value.strip() == '':
                    annotation = "[EMPTY]"
                elif cell_value.startswith('='):
                    annotation = "[FORMULA]"
                elif annotated_output.get(cell_id) and len(list(dict(annotated_output.get(cell_id)).values())) == 2:
                    annotation = f"[{list(dict(annotated_output.get(cell_id)).values())[-1]}] {cell_value}"
                else:
                    annotation = cell_value
                # Highlight the current cell
                formatted_value = annotation
                formatted_value = f"{{{formatted_value}}}" if cell_id == current_cell_id else formatted_value
                formatted_row.append(formatted_value)
            formatted_chunk.append(formatted_row)
        # Convert the chunk into a CSV string
        si = StringIO()
        cw = csv.writer(si)
        cw.writerows(formatted_chunk)
        return si.getvalue().strip()

    # Function to annotate cells using OpenAI
    def annotate_cells_ai(self, output_dict):
        openai.api_key = os.getenv('openai_api_key')
        iterator = 0
        size = 0

        for sheet in output_dict.values():
            for row in sheet.values():
                for chunk in row.values():
                    for cell in chunk['base_chunk']:
                        for cell_id, cell_value in cell:
                            if cell_value == ' ' or cell_value.startswith('='):
                                continue
                            size += 1

        for sheet_name, sheet in output_dict.items():
            annotated_output = {}
            original_csv_data = StringIO()
            writer = csv.writer(
                original_csv_data,
                delimiter=',',
                quoting=csv.QUOTE_MINIMAL)

            row_count = 0
            for row in sheet.values():
                for chunk in row.values():
                    for cell in chunk['base_chunk']:
                        row_data = []
                        for cell_id, cell_value in cell:
                            # Write the original CSV data
                            row_data.append(cell_value)
                            # Create a StringIO object to store the CSV data
                            csv_buffer = StringIO()
                            # Skip if the cell is empty or a formula
                            annotated_output[cell_id] = {'value': cell_value}
                            if cell_value.strip() == '' or cell_value.startswith('='):
                                if cell_value.strip() == '':
                                    annotated_output[cell_id]['annotation'] = 'EMPTY'
                                elif cell_value.startswith('='):
                                    annotated_output[cell_id]['annotation'] = 'FORMULA'
                                continue

                            # Get the annotated chunk string
                            chunk_str = self.get_annotated_chunk(
                                chunk['contextualized_chunk'], cell_id, annotated_output)

                            # Display the chunk to the user
                            reader = csv.reader(StringIO(chunk_str))
                            formatted_chunk = list(reader)

                            # Write the CSV data to the StringIO object
                            writer = csv.writer(
                                csv_buffer, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                            writer.writerows(formatted_chunk)

                            # Retrieve the CSV data from the StringIO object as a
                            # string
                            csv_data = csv_buffer.getvalue()

                            # Use OpenAI to predict if the cell is a label or data
                            prompt = constants.labeling_conversation + csv_data + \
                                f"Is cell {{{cell_value.strip()}}} in the following chunk a label cell? (Y/N)\n"
                            print(f"Cell {iterator}")
                            iterator += 1
                            print(
                                f"Prompt:\n{csv_data} Is cell {{{cell_value.strip()}}} in the following chunk a label cell? (Y/N)\n")
                            print(f"Cell {iterator}/{size}")
                            # response = openai.Completion.create(engine='text-davici-003', prompt=prompt, max_tokens=10)

                            # Generate a response using the conversation
                            completions = openai.Completion.create(
                                model="text-davinci-003",
                                # Determines the quality, speed, and cost.
                                temperature=0.5,            # Level of creativity in the response
                                prompt=prompt,           # What the user typed in
                                max_tokens=100,             # Maximum tokens in the prompt AND response
                                n=3,                        # The number of completions to generate
                                stop=None,                  # An optional setting to control response generation
                            )

                            # Get the assistant's reply
                            assistant_reply = completions.choices[0].text

                            #assistant_reply = 'Y'
                            # Print the assistant's reply
                            print(f"Reply: {assistant_reply}")
                            if 'Y' in assistant_reply:
                                annotated_output[cell_id]['annotation'] = 'LABEL'
                            else:
                                annotated_output[cell_id]['annotation'] = 'DATA'
                        # Increment row count and write to CSV buffer
                        row_count += 1
                        writer.writerow(row_data)
            #print(annotated_output)
            cells = []
            #convert annotated output to sheet
            for cell_id, cell in annotated_output.items():
                cells.append(cel(location=cell_id, value=cell['value'], annotation=cell['annotation']))
            #print(cells)
            self.cells = cells

    # Function to sort cells by block_type, group cells by block_type, create blocks using MaxAreaRectangles and add to sheet's blocks
    def sb_id(self):
        if (self.cells != []) and (self.cells != None):
            # Sort cells by block_type
            sorted_cells = sorted(self.cells, key=lambda cell: cell.block_type)

            # Group cells by block_type
            groups = {}
            for cell in sorted_cells:
                cell.coord = (cell.coord[0]+1, cell.coord[1]+1)
                if cell.block_type != "EMPTY":
                    if cell.block_type not in groups:
                        groups[cell.block_type] = []
                    groups[cell.block_type].append(cell)

            # Create blocks using MaxAreaRectangles and add to sheet's blocks
            self.blocks = []
            for block_type, cells_group in groups.items():
                # Create a grid representing the cells of this block_type
                grid = gth.create_grid(cells_group)

                # Find largest rectangles in the grid
                max_area_rectangles = MaxAreaRectangles(grid, print=False)
                rectangles = max_area_rectangles.find_largest_rectangles()

                # Create blocks from the found rectangles and add to the sheet's blocks
                for rectangle in rectangles:
                    x, y, width, height = rectangle
                    block_cells = [cell for cell in cells_group if x <= cell.coord[0] <= x + width and y <= cell.coord[1] <= y + height]
                    self.blocks.append(blk(block_cells, annotation_type=block_type))

            if self.blocks:
                self.free_labels = []
                self.free_data = []
                for block in self.blocks:
                    if block.annotation_type == "LABEL":
                        self.free_labels.append(block)
                    if block.annotation_type == "DATA":
                        self.free_data.append(block)
            else:
                self.blocks = []
                self.blocks.extend(self.free_labels)
                self.blocks.extend(self.free_data)

    # Function to get the expected positions of adjacent blocks around the border of the block
    def border_id(self, border_structures, base_structures, combined_structures, t=None, l=None, r=None, b=None, size_dependent=False):
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
                        border_structure = unused_border_structures.get(border_ep)
                        if border_structure:
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
                        table.data_block = base_structure
                        # If the border structure is a label block, add it as a label block border
                        if border_structure.annotation_type == "LABEL":
                            keys = ['l0', 'l1', 'r0', 'r1', 't0', 't1', 'b0', 'b1']

                            #Iterate through label block locations
                            for key in keys:
                                direction = 'same_height' if key[0] in ['l', 'r'] else 'same_width'
                                table.label_blocks[direction][key] = dimension.get(base_structure.border_eps[direction][key])

                        # If the border structure is a data block, add it as a free block
                        elif border_structure.annotation_type == "DATA":
                            table.free_blocks.append(border_structure)

                    # If the base structure is a label block, add it as a free block
                    elif base_structure.annotation_type == "LABEL":
                        table.free_blocks.append(base_structure)
                        # Add the border structure as a free block, regardless of its annotation type
                        if border_structure.annotation_type == "LABEL" or border_structure.annotation_type == "DATA":
                            table.free_blocks.append(border_structure)

                    # If the base structure is a table, add it as a subtable
                    elif isinstance(base_structure, tbl):
                        table.subtables.append(base_structure)
                        # Add the border structure according to its type
                        if border_structure.annotation_type == "LABEL":
                            keys = ['l0', 'l1', 'r0', 'r1', 't0', 't1', 'b0', 'b1']

                            #Iterate through label block locations
                            for key in keys:
                                direction = 'same_height' if key[0] in ['l', 'r'] else 'same_width'
                                table.label_blocks[direction][key] = dimension.get(base_structure.border_eps[direction][key])

                        elif border_structure.annotation_type == "DATA":
                            table.free_blocks.append(border_structure)
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

    #Solid Table Identification: groups together adjacent free blocks and/or tables into larger tables
    def st_id(self):
        self.border_id(border_structures=self.free_labels, base_structures=self.free_data, combined_structures=self.tables)

    #Light Block Identification: Finds blocks that are not part of a table due to their size mismatch within the border eps
    def lb_id(self):
        #lb ab
        #lb bb
        #lb cb
        #lb label
        pass

    #Solid Table Identification 2: groups together adjacent free blocks and/or tables into larger tables
    def st_id2(self):
        # Initialize a dictionary to store leftover structures
        leftover_structs = {}

        # Initialize a dictionary to store block or table ep coordinates
        struct_coords = {}

        # Initialize a dictionary to store higher level tables, using data coordinates as keys
        higher_level_table_dict = {}

        #Fix all below this to work with structs generally
        # Create a hashmap mapping label coordinate tuples to free label blocks
        for label_block in self.free_labels:
            leftover_structs[label_block.expected_position] = label_block

        # Initialize a nested dictionary for storing position data
        pos_dict = {
            'same_height':{"l0": {}, "l1": {}, "r0": {}, "r1": {}}, 
            'same_width': {"t0": {}, "t1": {}, "b0": {}, "b1": {}}
        }

        # Iterate over data blocks in the Sheet
        for data_block in self.free_data:
            # Get the border coordinates for each data block
            label_eps = data_block.border_eps
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
            for data_coord, label in pos_dict[pos[0]][pos[1]].items():
                if label.expected_position in leftover_labels.keys():
                    # Create a new table if it doesn't already exist in the table dictionary
                    if not (data_coord in table_dict.keys()):
                        table_dict[data_coord] = tbl(data_block=data_coords[data_coord])
                        self.free_data.remove(data_coords[data_coord])

                    # Set the attribute of the table according to the current position
                    table_dict[data_coord].label_blocks[pos[0]][pos[1]] = leftover_labels[label.expected_position]
                    # Remove used labels from leftover_labels
                    leftover_labels.pop(label.expected_position)
                    self.free_labels.remove(label)

        # Add processed sheet to sheet_dict
        self.tables=table_dict.values()
    
    def check_df_ep(self, df):
        # Initialize a dictionary to store the mismatches
        mismatches = {}

        # Check for mismatches in the free labels
        for free_label in self.free_labels:
            free_label_check_result = free_label.check_df_ep(df)
            if free_label_check_result != True:
                # If there are mismatches, update the mismatches dictionary
                mismatches.update(free_label_check_result)

        # Check for mismatches in the free data blocks
        for free_data_block in self.free_data:
            free_data_check_result = free_data_block.check_df_ep(df)
            if isinstance(free_data_check_result, dict):
                for coord, value in free_data_check_result.items():
                    cell = next((cell for cell in free_data_block.cells if cell.coord == coord), None)
                    if cell is not None:
                        cell.value = value

        # Check for mismatches in all tables
        for table in self.tables:
            table_check_result = table.check_df_ep(df)
            if table_check_result != True:
                # If there are mismatches, update the mismatches dictionary
                mismatches.update({table.expected_position: table_check_result})

        # Return the mismatches dictionary
        return mismatches

class constants:
    labeling_conversation = """{Property Name},Property Type,Price,Square Feet,Bedrooms
White House,Single Family,2000000,10000,6
Empire State,Apartment,1000000,4000,2
Sydney Tower,Condominium,3000000,15000,4
[EMPTY]  ,[EMPTY]  ,[EMPTY]  ,[EMPTY]  ,[EMPTY]
 Is cell {Property Name} a label cell? (Y/N)

Y

[LABEL] Property Name,{Property Type},Price,Square Feet,Bedrooms
White House,Single Family,2000000,10000,6
Empire State,Apartment,1000000,4000,2
Sydney Tower,Condominium,3000000,15000,4
[EMPTY]  ,[EMPTY]  ,[EMPTY]  ,[EMPTY]  ,[EMPTY]
 Is cell {Property Type} a label cell? (Y/N)

Y

[LABEL] Property Name,[LABEL] Property Type,[LABEL] Price,[LABEL] Square Feet,[LABEL] Bedrooms
{White House},Single Family,2000000,10000,6
Empire State,Apartment,1000000,4000,2
Sydney Tower,Condominium,3000000,15000,4
[EMPTY]  ,[EMPTY]  ,[EMPTY]  ,[EMPTY]  ,[EMPTY]
 Is cell {White House} a label cell? (Y/N)

N

[LABEL] Property Name,[LABEL] Property Type,[LABEL] Price,[LABEL] Square Feet,[LABEL] Bedrooms
[DATA] White House,[DATA] Single Family,{2000000},10000,6
Empire State,Apartment,1000000,4000,2
Sydney Tower,Condominium,3000000,15000,4
[EMPTY]  ,[EMPTY]  ,[EMPTY]  ,[EMPTY]  ,[EMPTY]
 Is cell {2000000} a label cell? (Y/N)

N
"""
