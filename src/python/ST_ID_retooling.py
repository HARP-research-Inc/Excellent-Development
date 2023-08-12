from structures.gen_tree import Gen_Tree as gen_tree
from structures.cell import Cell as cell
from structures.sheet import Sheet as sheet
from structures.block import Block as block
from prompt_interface import prompt_interface
import os
import json

def st_id(Sheets_dict: dict, debug=True):
    #take in Sheets_dict
    #for all data Blocks: ask AI if table nearby
    #ask AI for table from datablock
    st_Sheets = {}
    for name, Sheet in Sheets_dict.items():
        # Initialize Sheet
        Sheet = initialize_Sheets(Sheet)
        if debug:
            print(f"Initialized Sheet: {name}")
            print("\tData: ")
            for Block in Sheet['Blocks']:
                print_Block(Block)
            print("\tSorted Labels: ")
            for coord in ['x', 'y']:
                print(f"\t---By {coord}---")
                for length in Sheet['labels_by_x_y'][coord]:
                    print(f"\n\tLength: {length}")
                    for Block in Sheet['labels_by_x_y'][coord][length]:
                        print_Block(Block)
        # Identify Tables
        st_Sheets[Sheet['Sheet_number']] = connect_labels(Sheet)
        if debug:
            print_output(st_Sheets[Sheet['Sheet_number']])
    return st_Sheets


def excel_column_number(column):
    # function for turning columns letters into numbers
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


def initialize_Sheets(Sheet):
    # initializes a Sheet
    Sheet['labels_by_x_y'] = {'x': {}, 'y': {}}
    for Block_type in [Sheet['free_labels'],Sheet['free_data']]:
        for Block in Block_type:
            # organize labels into dictionaries by size
            if Block_type == Sheet['free_labels']:
                for coord in ['x', 'y']:
                    if not (
                            Block[f'{coord}_size'] in Sheet['labels_by_x_y'][coord]):
                        Sheet['labels_by_x_y'][coord][Block[f'{coord}_size']] = [
                        ]
                    Sheet['labels_by_x_y'][coord][Block[f'{coord}_size']].append(
                        Block)
            # set starting position for potential labels for data Blocks
            elif Block_type == Sheet['free_data']:
                Block['start_pos'] = {}
                Block['start_pos']['l0'] = [
                    Block['start_column'] - 1, Block['start_row']]
                Block['start_pos']['l1'] = [
                    Block['start_column'] - 2, Block['start_row']]
                Block['start_pos']['r0'] = [
                    Block['end_column'] + 1, Block['start_row']]
                Block['start_pos']['r1'] = [
                    Block['end_column'] + 2, Block['start_row']]
                Block['start_pos']['t0'] = [
                    Block['start_column'], Block['start_row'] - 1]
                Block['start_pos']['t1'] = [
                    Block['start_column'], Block['start_row'] - 2]
                Block['start_pos']['b0'] = [
                    Block['start_column'], Block['end_row'] + 1]
                Block['start_pos']['b1'] = [
                    Block['start_column'], Block['end_row'] + 2]
                for pos in Block['start_pos'].keys():
                    for i in [0, 1]:
                        if Block['start_pos'][pos][i] < 0:
                            Block['start_pos'][pos][i] = None
            else:
                raise ValueError("Empty Sheet")

    # organize data Blocks by size
    Sheet['Blocks'] = sorted(
        Sheet['Blocks']['DATA'],
        key=lambda k: (
            k['y_size'],
            k['x_size']))
    # organize label Blocks by size
    for coord in ['x', 'y']:
        for length in Sheet['labels_by_x_y'][coord].keys():
            Sheet['labels_by_x_y'][coord][length] = sorted(
                Sheet['labels_by_x_y'][coord][length], key=lambda x: x[f'{coord}_size'])
    # return modified Sheet
    return Sheet


def connect_labels(Sheet, debug=False):
    # check label Block connections by data Block
    LBs = [label for length in Sheet['labels_by_x_y']['x']
           for label in Sheet['labels_by_x_y']['x'][length]]
    st_annotated_Sheet = {
        'solid_tables': [],
        'free_solid_Blocks': {
            'LABEL': LBs,
            'DATA': Sheet['Blocks']}}
    data_Blocks = st_annotated_Sheet['free_solid_Blocks']['DATA']
    labels_by_x_y = Sheet['labels_by_x_y']
    LB_connects = {}
    LB_tuples = {}

    # find potential label data connections
    for DB in data_Blocks:
        start_poses = {}
        for key in list(DB['start_pos'].keys()):
            start_poses[tuple(DB['start_pos'][key])] = str(key)
        # invert positions so potential coordinate tuples are keys and position
        # types are values
        if (DB['y_size'] in labels_by_x_y['y']) or (
                DB['x_size'] in labels_by_x_y['x']):
            # if LB's with correct height or wdith
            for LB in LBs:
                # iterate through all label Blocks, organized by width
                ls = tuple(LB['pos']['start'])
                # creates a hashable dictionary to look up label Blocks
                LB_tuples[ls] = LB
                # set ls to the top left coord of label Block
                if ls in start_poses:
                    # if label overlaps with potential connection area
                    if ls not in LB_connects:
                        LB_connects[ls] = {}
                        # if label pos not in LB_connects, make new dict
                    LB_connects[ls][start_poses[ls]] = DB
                    # set potential LB connection in dictionary to a data Block
                    st_annotated_Sheet['free_solid_Blocks']['LABEL'].remove(LB)
                    # remove the LB from the list
                    if DB in st_annotated_Sheet['free_solid_Blocks']['DATA']:
                        st_annotated_Sheet['free_solid_Blocks']['DATA'].remove(
                            DB)
                    # remove the DB from the list if it hasnt already been

    if debug:
        print(LB_connects)
    # sort through potential connections,
    # limit to the highest according to the ordered check_poses list of connection types
    # add to solid table Sheet
    check_poses = ['l0', 'l1', 'r0', 'r1', 't0', 't1', 'b0', 'b1']
    for LB_tuple in LB_connects:
        connection = ''
        # init connection type variable
        if len(LB_connects[LB_tuple].values()) > 1:
            connection = sorted(
                LB_connects[LB_tuple].keys(),
                key=lambda x: check_poses.index(x))[0]
            # if multiple potential connections, choose the highest ranked
        else:
            connection = list(LB_connects[LB_tuple].keys())[0]
            # set connection
        DB = LB_connects[LB_tuple][connection]
        # get data Block for connection
        LB = LB_tuples[LB_tuple]
        for ST in st_annotated_Sheet['solid_tables']:
            if DB == ST['data']:
                ST['labels'][connection] = LB
                # for all current tables, if there is one with this DB then add
                # this LB connection to it
        if not any(DB == ST['data']
                   for ST in st_annotated_Sheet['solid_tables']):
            st_annotated_Sheet['solid_tables'].append(
                {'data': DB, 'labels': {connection: LB}})
            # if no ST's with a given data Block, make a new one

    return st_annotated_Sheet


def print_Block(Block):
    print(f"\t{Block['x_size']}x{Block['y_size']}\tStart: {excel_column_letter(Block['pos']['start'][0])}{Block['pos']['start'][1]}")
    print(
        f"\t\tEnd: {excel_column_letter(Block['pos']['end'][0])}{Block['pos']['end'][1]}\n")


def print_output(st_annotated_Sheet: dict):
    # go through ST annotated Sheet dicts and print for validation
    print("Solid Tables:")
    for ST in st_annotated_Sheet['solid_tables']:
        print("\tData:")
        print_Block(ST['data'])
        # print the corners of each dataBlock
        print("\tLabels:")
        for key, value in ST['labels'].items():
            print(f"\t\t{key}: ")
            print_Block(value)
        # print the corners of each label Block
    print("Free Blocks: ")
    for type in ['LABEL', 'DATA']:
        print(f"\t{type} Blocks:")
        for Block in st_annotated_Sheet['free_solid_Blocks'][type]:
            print_Block(Block)


def write_json(output_data, output_file):
    # write output to a json file
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)


