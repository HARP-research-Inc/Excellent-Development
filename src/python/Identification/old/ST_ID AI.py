import json

def excel_column_number(column):
    num = 0
    for c in column:
        if c.isalpha():
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num

def read_in_json(json_file):
    # read in json and parse into dictionaries
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

def convert_coords(sheets):
    # convert columns from string to int
    for sheet in sheets:
        for block_type in sheet['blocks']:
            for block in sheet['blocks'][block_type]:
                block['start_column'] = excel_column_number(block['start_column'])
                block['end_column'] = excel_column_number(block['end_column'])
    return sheets

def measure_dsbs_and_lsbs(sheets):
    # record size of all data and label solid blocks and add to SBs dict
    for sheet in sheets:
        for block_type in sheet['blocks']:
            for block in sheet['blocks'][block_type]:
                # calculate the size of the block
                block['x_size'] = block['end_column'] - block['start_column'] + 1
                block['y_size'] = block['end_row'] - block['start_row'] + 1
    return sheets

def organize_sbs_by_size(sheets):
    # reorganize data SBs by size to start with the smallest
    for sheet in sheets:
        # sorting blocks by y_size then by x_size
        sheet['blocks']['DATA'] = sorted(sheet['blocks']['DATA'], key=lambda k: (k['y_size'], k['x_size']))
    return sheets

# Define the data block structure
class DataBlock:
    def __init__(self, start_row, end_row, start_column, end_column):
        self.start_row = start_row
        self.end_row = end_row
        self.start_column = start_column
        self.end_column = end_column
        self.x_size = end_column - start_column + 1
        self.y_size = end_row - start_row + 1
        self.positioned_dbs = []
        self.generate_available_places()
        
    # generate coords of available starting and ending positions
    def generate_available_places(self):
        self.start_pos_l0 = self.start_column - 1
        self.start_pos_l1 = self.start_column - 2
        self.start_pos_r0 = self.end_column + 1
        self.start_pos_r1 = self.end_column + 2
        self.start_pos_t0 = self.start_row - 1
        self.start_pos_t1 = self.start_row - 2
        self.start_pos_b0 = self.end_row + 1
        self.start_pos_b1 = self.end_row + 2

def check_labels(data_SBs, labels_by_x_y):
    # check label block connections by data block
    pass

def check_x_coordinates_of_available_labels(sheet):
    # check coords of label SBs to find potential options
    pass

def generate_available_places(data_SBs):
    # generate coords of available starting and ending positions
    pass

def check_potentials_against_options(data_SBs, labels_by_x_y):
    # check all potentials against options given
    pass

def fill_right_potentials(st_annotated_sheets):
    # add all nonremoved right_potentials STs
    pass

def fill_free_blocks(horiz_data_SBs, horiz_labels_by_x_y):
    # add all non-removed free blocks to the free blocks
    pass

def check_y_coordinates_of_available_labels(st_annotated_sheets, data_SBs):
    # check coords of label SBs to find potential options
    pass

def print_output(st_annotated_sheets):
    # go through ST annotated sheet dicts and print for validation
    pass

def write_json(output_data, output_file):
    # write output to a json file
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)

# Load json data
data = read_in_json("blocks_output.json")

# Convert coordinates
sheets = convert_coords(data)

# Rest of your script implementation goes here...
