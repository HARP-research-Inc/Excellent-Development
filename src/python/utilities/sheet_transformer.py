 #? Title: sheet_transformer.py
 # Author: Harper Chisari

#? Contents:
#   CLASS - Sheet_Transformer: Contains all algorithmic transformations and pre-processing for a sheet
#       #!LAST TESTED: 8/17/23
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
#   Harper: 8/17/23 - V1.1 - added border_id and redid/completed title block, moved border_id method to utilities/border_id.py
#   Harper: 8/16/23 - V1.0 - initial commit


import sys
import openai, os, csv
from io import StringIO


if 'pytest' in sys.modules:
    from src.python.utilities.gen_tree_helper import Gen_Tree_Helper as gth
    from src.python.utilities.max_area_rectangles import MaxAreaRectangles
    from src.python.utilities.border_id import Border_Interaction_and_Identification as bii
    from src.python.structures.cell import Cell as cel
    from src.python.structures.block import Block as blk
    #from src.python.structures.table import Table as tbl
else:
    from utilities.gen_tree_helper import Gen_Tree_Helper as gth
    from utilities.max_area_rectangles import MaxAreaRectangles
    from utilities.border_id import Border_Interaction_and_Identification as bii
    from structures.cell import Cell as cel
    from structures.block import Block as blk
    #from structures.table import Table as tbl


class Sheet_Transformer:

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
                            chunk_str = gth.get_annotated_chunk(
                                chunk['contextualized_chunk'], cell_id, annotated_output=annotated_output)

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

    # Solid Block Identification: Function to sort cells by block_type, group cells by block_type, create blocks using MaxAreaRectangles and add to sheet's blocks
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

    # Solid Table Identification: groups together adjacent free blocks and/or tables into larger tables
    def st_id(self):
        bii(border_structures=self.free_labels, base_structures=self.free_data, combined_structures=self.tables, ).border_id()

    # Light Block Identification: Finds blocks that are not part of a table due to their size mismatch within the border eps
    def lb_id(self):
        # for the following, pass tables as combined_structures

        # lb label:
        # use tables as base, find labels within border eps of tables with size flexible on and standard distances.
        bii(border_structures=self.free_labels, base_structures=self.tables, combined_structures=self.tables, size_flexible=(True, True)).border_id()

        # lb ab:
        # use free labels as base and search for data blocks smaller than the label blocks, with search parameters size_flexible x
        bii(border_structures=self.free_data, base_structures=self.free_labels, combined_structures=self.tables, size_flexible=(True, False)).border_id()

        # lb bb:
        # use free labels as base and search for data blocks smaller than the label blocks, with search parameters size_flexible y
        bii(border_structures=self.free_data, base_structures=self.free_labels, combined_structures=self.tables, size_flexible=(False, True)).border_id()

        # lb cb:
        # use free data as base and search for datablocks near other datablocks with size_flexible x and y
        bii(border_structures=self.free_data, base_structures=self.free_data, combined_structures=self.free_data, size_flexible=(True, True)).border_id()
        bii(border_structures=self.free_data, base_structures=self.free_data, combined_structures=self.tables, size_flexible=(True, True)).border_id()

        # use tables as base, search for label blocks with default size constraints.
        bii(border_structures=self.free_labels, base_structures=self.tables, combined_structures=self.tables, size_flexible=(True, True)).border_id()

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
