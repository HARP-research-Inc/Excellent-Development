import json

def excel_column_number(column):
    #function for turning columns letters into numbers 
    num = 0
    for c in column:
        if c.isalpha():
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num

def excel_column_letter(column_number):
    # Function for turning column numbers into letters
    letters = []
    while column_number > 0:
        column_number, remainder = divmod(column_number - 1, 26)
        letters.insert(0, chr(remainder + ord('A')))
    return ''.join(letters)

def read_in_json(json_file):
    # read in json and parse into dictionaries
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

def initialize_sheets(sheet):
    #initializes a sheet
    sheet['labels_by_x_y'] = {'x':{}, 'y':{}}
    for block_type in sheet['blocks']:
        for block in sheet['blocks'][block_type]:
            # convert columns from string to int
            block['start_column'] = excel_column_number(block['start_column'])
            block['end_column'] = excel_column_number(block['end_column'])
            # calculate the size of the block
            block['x_size'] = block['end_column'] - block['start_column'] + 1
            block['y_size'] = block['end_row'] - block['start_row'] + 1
            block['pos'] = {'start':[block['start_column'], block['start_row']], 'end':[block['end_column'], block['end_row']]}
            #organize labels into dictionaries by size
            if str(block_type) == 'LABEL':
                for coord in ['x','y']:
                    if not (block[f'{coord}_size'] in sheet['labels_by_x_y'][coord]):
                        sheet['labels_by_x_y'][coord][block[f'{coord}_size']] = []
                    sheet['labels_by_x_y'][coord][block[f'{coord}_size']].append(block)
            #set starting position for potential labels for data blocks
            elif str(block_type) == 'DATA':
                block['start_pos'] = {}
                block['start_pos']['l0'] = [block['start_column'] - 1,  block['start_row']      ]
                block['start_pos']['l1'] = [block['start_column'] - 2,  block['start_row']      ]
                block['start_pos']['r0'] = [block['end_column'] + 1,    block['start_row']      ]
                block['start_pos']['r1'] = [block['end_column'] + 2,    block['start_row']      ]
                block['start_pos']['t0'] = [block['start_column'],      block['start_row'] - 1  ]
                block['start_pos']['t1'] = [block['start_column'],      block['start_row'] - 2  ]
                block['start_pos']['b0'] = [block['start_column'],      block['end_row'] + 1    ]
                block['start_pos']['b1'] = [block['start_column'],      block['end_row'] + 2    ]
                for pos in block['start_pos'].keys():
                    for i in [0,1]:
                        if block['start_pos'][pos][i] < 0:
                            block['start_pos'][pos][i] = None
            else:
                raise ValueError("Unexpected Block Type")
    #organize data blocks by size
    sheet['blocks'] = sorted(sheet['blocks']['DATA'], key=lambda k: (k['y_size'], k['x_size']))
    #organize label blocks by size
    for coord in ['x','y']:
        for length in sheet['labels_by_x_y'][coord].keys():
            sheet['labels_by_x_y'][coord][length] = sorted(sheet['labels_by_x_y'][coord][length], key=lambda x: x[f'{coord}_size'])
    #return modified sheet
    return sheet

def connect_labels(sheet, debug = False):
    # check label block connections by data block
    LBs = [label for length in sheet['labels_by_x_y']['x'] for label in sheet['labels_by_x_y']['x'][length]]
    st_annotated_sheet = {'solid_tables' : [], 'free_solid_blocks': {'LABEL':LBs,'DATA':sheet['blocks']}}
    data_blocks = st_annotated_sheet['free_solid_blocks']['DATA']
    labels_by_x_y = sheet['labels_by_x_y']
    LB_connects = {}
    LB_tuples = {}

    #find potential label data connections
    for DB in data_blocks:
        start_poses = {}
        for key in list(DB['start_pos'].keys()):
            start_poses[tuple(DB['start_pos'][key])] = str(key)
        #invert positions so potential coordinate tuples are keys and position types are values
        if (DB['y_size'] in labels_by_x_y['y']) or (DB['x_size'] in labels_by_x_y['x']):
            #if LB's with correct height or wdith
            for LB in LBs:
                #iterate through all label blocks, organized by width
                ls = tuple(LB['pos']['start'])
                #creates a hashable dictionary to look up label blocks
                LB_tuples[ls] = LB
                #set ls to the top left coord of label block
                if ls in start_poses:
                    #if label overlaps with potential connection area
                    if not ls in LB_connects:
                        LB_connects[ls] = {}
                        #if label pos not in LB_connects, make new dict
                    LB_connects[ls][start_poses[ls]] = DB 
                    #set potential LB connection in dictionary to a data block
                    st_annotated_sheet['free_solid_blocks']['LABEL'].remove(LB) 
                    #remove the LB from the list
                    if DB in st_annotated_sheet['free_solid_blocks']['DATA']: st_annotated_sheet['free_solid_blocks']['DATA'].remove(DB) 
                    #remove the DB from the list if it hasnt already been

    if debug:
        print(LB_connects)
    #sort through potential connections,
    #limit to the highest according to the ordered check_poses list of connection types
    #add to solid table sheet
    check_poses = ['l0','l1','r0','r1','t0','t1','b0','b1']
    for LB_tuple in LB_connects:
        connection = ''
        #init connection type variable
        if len(LB_connects[LB_tuple].values()) > 1:
            connection = sorted(LB_connects[LB_tuple].keys(), key=lambda x: check_poses.index(x))[0]
            #if multiple potential connections, choose the highest ranked
        else:
            connection = list(LB_connects[LB_tuple].keys())[0]
            #set connection
        DB = LB_connects[LB_tuple][connection]
        #get data block for connection
        LB = LB_tuples[LB_tuple]
        for ST in st_annotated_sheet['solid_tables']:
            if DB == ST['data']:
                ST['labels'][connection] = LB
                #for all current tables, if there is one with this DB then add this LB connection to it
        if not any(DB == ST['data'] for ST in st_annotated_sheet['solid_tables']):
            st_annotated_sheet['solid_tables'].append({'data': DB, 'labels': {connection: LB}})
            #if no ST's with a given data block, make a new one
            
    return st_annotated_sheet

def print_block(block):
    print(f"\t{block['x_size']}x{block['y_size']}\tStart: {excel_column_letter(block['pos']['start'][0])}{block['pos']['start'][1]}")
    print(f"\t\tEnd: {excel_column_letter(block['pos']['end'][0])}{block['pos']['end'][1]}\n")

def print_output(st_annotated_sheet: dict):
    # go through ST annotated sheet dicts and print for validation
    print("Solid Tables:")
    for ST in st_annotated_sheet['solid_tables']:
        print(f"\tData:")
        print_block(ST['data'])
        #print the corners of each datablock
        print(f"\tLabels:")
        for key, value in ST['labels'].items():
            print(f"\t\t{key}: ")
            print_block(value)
        #print the corners of each label block
    print(f"Free Blocks: ")
    for type in ['LABEL', 'DATA']:
        print(f"\t{type} Blocks:")
        for block in st_annotated_sheet['free_solid_blocks'][type]:
            print_block(block)

def write_json(output_data, output_file):
    # write output to a json file
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)

def initialize_tabulate_and_export(input_filename = "JSONs/blocks_output.json", output_filename = "JSONs/solid_table_output.json", debug = True):
    # Load json data
    sheets = read_in_json(input_filename)
    st_sheets = {}
    for sheet in sheets:
        #Initialize Sheet
        sheet = initialize_sheets(sheet)
        if debug == True:  
            print(f"Initialized Sheet: {sheet['sheet_number']}")
            print(f"\tData: ")
            for block in sheet['blocks']:
                print_block(block)
            print(f"\tSorted Labels: ")
            for coord in ['x','y']:
                print(f"\t---By {coord}---")
                for length in sheet['labels_by_x_y'][coord]:
                    print(f"\n\tLength: {length}")
                    for block in sheet['labels_by_x_y'][coord][length]:
                        print_block(block)
        #Identify Tables
        st_sheets[sheet['sheet_number']] = connect_labels(sheet)
        if debug == True:
            print_output(st_sheets[sheet['sheet_number']])
    write_json(st_sheets, output_filename)

