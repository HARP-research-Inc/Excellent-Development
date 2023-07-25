from gen_tree import cell, sheet, block, gen_tree
from prompt_interface import prompt_interface
import os
import json

#python3.9 -m pytest -vv tests/test_demo_step_0-2.py 
#examples of I/O
data_examples = [
            {
                "user": {"csv": """' ', [DATA] 'A'\n' ', [DATA] 'B'\n' ', [DATA] 'C'"""}, 
                "assistant": {"json": """[{"start": "(1, 2)","end": "(1, 2)","cells": {"(2, 1)": {"value": "A", "annotation": "DATA"}, "(2, 2)": {"value": "B", "annotation": "DATA"},"(2, 3)": {"value": "C", "annotation": "DATA"}, "size": "(1, 1)"}}]"""}
            }]
#input: 
"""
' ', ' ', ' '
[DATA] 'El Ranchero', [DATA] 'Industrial', [DATA] '10/23/2015'
[DATA] 'The Appartments on the Hudson', [DATA] 'Residential', [DATA] '07/15/2016'
"""

"""
[
    {
        "start": "(2, 1)",
        "end": "(3, 3)",
        "cells": {
            "(2, 1)": {
                "value": 
                "El Ranchero",
                "annotation": 
                "DATA"
                },
            "(2, 2)": {
                "value": "Industrial",
                "annotation": "DATA"
                },
            "(2, 3)": {
                "value": "10/23/2015",
                "annotation": "DATA"
                },
            "(3, 1)": {
                "value": "The Appartments on the Hudson",
                "annotation": "DATA"
                },
            "(3, 2)": {
                "value": "Residential",
                "annotation": "DATA"
                },
            "(3, 3)": {
                "value": "07/15/2016",
                "annotation": "DATA"
                }
            },
        "size": "(2, 3)"
        }
    ]
"""

labels_examples = [
            {
                "user": {"csv": """[LABEL] '1', ' '\n[LABEL] '2', ' '\n' ', ' '"""}, 
                "assistant": {"json": """[{"start": "(1, 1)","end": "(1, 2)","cells": {"(1, 1)": {"value": "1", "annotation": "LABEL"},"(1, 2)": {"value": "2","annotation": "LABEL"}},"size": "(1, 2)"},]"""}
            },
            {
                "user": {"csv": """[LABEL] 'Property Name', [LABEL] 'Property Type', [LABEL] 'Date Acquired'\n' ', ' ', ' '\n' ', ' ', ' '"""}, 
                "assistant": {"json": """[{"start": "(1, 1)","end": "(1, 3)","cells": {"(1, 1)": {"value": "Property Name","annotation": "LABEL"},"(1, 2)": {"value": "Property Type","annotation": "LABEL"},"(1, 3)": {"value": "Date Acquired","annotation": "LABEL"}},"size": "(1, 3)"}]"""}
            }
        ]
def sb_id(sheets):
    #* SB_sheets will store the processed sheets
    SB_sheets = {}
    
    #* Loop through all the sheets
    for name, cell_dict in sheets.items():
        labels = []
        data = []
        redo_dict = {}
        
        #* Update redo_dict with cell_dict
        redo_dict.update(cell_dict)
        
        #* Loop through all the cells in the sheet
        for coord, Cell in redo_dict.items():
            #* Skip cells with 'EMPTY' annotation
            if Cell['annotation'] == 'EMPTY':
                continue
            
            #* Create a block for each cell
            Block = block(cells=[cell(location=coord, value=Cell['value'],annotation=Cell['annotation'])])
            
            #* Check if the block annotation is 'LABEL' or 'DATA' and add it to the appropriate list
            if Block.annotation_type == "LABEL":
                labels.append(Block)
            if Block.annotation_type == "DATA":
                data.append(Block)
        
        #* Create a sheet for labels and data
        label_cur_sheet = sheet(name=name, free_labels=labels)
        data_cur_sheet = sheet(name=name, free_data=data)

        k_map = []
        for i in range(len(data_cur_sheet)):
            k_map.append([])
            for j in range(len(data_cur_sheet[i])):
                if data_cur_sheet.cells == 'EMPTY' or data_cur_sheet.blocks == 'LABEL':
                    k_map[i][j] = 0
                else:
                    k_map[i][j] = 1
    
    #! =========================================================================================
    #! Starting from here, this is the prompt AI method that will be replaced with an algorithm
    #! =========================================================================================
    '''
        #* Get CSV representation of the labels and data
        label_csv = label_cur_sheet.get_csv()
        data_csv = data_cur_sheet.get_csv()
        
        #* Get OpenAI API Key
        openai_api_key = os.getenv('openai_api_key')
        
        #* Define variables to send for prompts
        label_variables = {"in":{"csv":label_csv},"out":["json"]}
        data_variables = {"in":{"csv":data_csv},"out":["json"]}
        
        #* Define the input structure for the prompt
        input_structure = "Consolidate the following annotated csv into a json with uninteruppted blocks: {csv}"
        
        #* Define examples to be used for the prompt
        #* Note: Examples should be varied and represent all possible use cases
        data_examples = [
            {
                "user": {"csv": """' ', [DATA] 'A'\n' ', [DATA] 'B'\n' ', [DATA] 'C'"""}, 
                "assistant": {"json": """[{"start": "(1, 2)","end": "(1, 2)","cells": {"(2, 1)": {"value": "A", "annotation": "DATA"}, "(2, 2)": {"value": "B", "annotation": "DATA"},"(2, 3)": {"value": "C", "annotation": "DATA"}, "size": "(1, 1)"}}]"""}
            },
            {
                "user": {"csv": """' ', ' ', ' '\n[DATA] 'El Ranchero', [DATA] 'Industrial', [DATA] '10/23/2015'\n[DATA] 'The Appartments on the Hudson', [DATA] 'Residential', [DATA] '07/15/2016'"""}, 
                "assistant": {"json": """[{"start": "(2, 1)","end": "(3, 3)","cells": {"(2, 1)": {"value": "El Ranchero","annotation": "DATA"},"(2, 2)": {"value": "Industrial","annotation": "DATA"},"(2, 3)": {"value": "10/23/2015","annotation": "DATA"},"(3, 1)": {"value": "The Appartments on the Hudson","annotation": "DATA"},"(3, 2)": {"value": "Residential","annotation": "DATA"},"(3, 3)": {"value": "07/15/2016","annotation": "DATA"}},"size": "(2, 3)"}]"""}
            }
        ]
        labels_examples = [
            {
                "user": {"csv": """[LABEL] '1', ' '\n[LABEL] '2', ' '\n' ', ' '"""}, 
                "assistant": {"json": """[{"start": "(1, 1)","end": "(1, 2)","cells": {"(1, 1)": {"value": "1", "annotation": "LABEL"},"(1, 2)": {"value": "2","annotation": "LABEL"}},"size": "(1, 2)"},]"""}
            },
            {
                "user": {"csv": """[LABEL] 'Property Name', [LABEL] 'Property Type', [LABEL] 'Date Acquired'\n' ', ' ', ' '\n' ', ' ', ' '"""}, 
                "assistant": {"json": """[{"start": "(1, 1)","end": "(1, 3)","cells": {"(1, 1)": {"value": "Property Name","annotation": "LABEL"},"(1, 2)": {"value": "Property Type","annotation": "LABEL"},"(1, 3)": {"value": "Date Acquired","annotation": "LABEL"}},"size": "(1, 3)"}]"""}
            }
        ]

        #* Call the prompt interface to generate json data for data and labels
        json_SB_data = prompt_interface(openai_api_key=openai_api_key, variables=data_variables, input_structure=input_structure, examples=data_examples)['json']
        json_SB_labels = prompt_interface(openai_api_key=openai_api_key, variables=label_variables, input_structure=input_structure, examples=labels_examples)['json']
        
        #* Create a new sheet
        SB_sheet = sheet(name=name)
        
        #* Loop through all blocks in the data json and add it to the sheet's data blocks
        for Block in json.loads(json_SB_data):
            cells = {}
            for coord, Cell in Block['cells'].items():
                if Cell['annotation'] != "EMPTY":
                    cells[coord]=Cell
            Block['cells']=cells
            new_block = block.from_json(Block)
            if new_block.annotation_type == "DATA":
                SB_sheet.free_data.append(new_block)
        
        #* Loop through all blocks in the labels json and add it to the sheet's label blocks
        for Block in json.loads(json_SB_labels):
            cells = {}
            for coord, Cell in Block['cells'].items():
                if Cell['annotation'] != "EMPTY":
                    cells[coord]=Cell
            Block['cells']=cells
            new_block = block.from_json(Block)
            if new_block.annotation_type == "LABEL":
                SB_sheet.free_labels.append(new_block)
        
        #* Add the processed sheet to SB_sheets
        SB_sheets[name] = SB_sheet
    
    #* Generate the tree for all sheets
    SB_tree = gen_tree(sheets = SB_sheets)
    
    #* Return the generated tree
    return SB_tree
    '''
    #! =========================================================================================
    #! Starting from here, this is the beginning of the algorithmic method to sheet blocks
    #! =========================================================================================
    
    def find_groups_of_ones(K_map):
        rows = len(K_map)
        cols = len(K_map[0])
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        groups = []

        def dfs(row, col, group):
            if row < 0 or row >= rows or col < 0 or col >= cols:
                return
            if visited[row][col] or K_map[row][col] == 0:
                return

            visited[row][col] = True
            group.append((row, col))

            # Check neighboring cells
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                dfs(row + dr, col + dc, group)

        for row in range(rows):
            for col in range(cols):
                if not visited[row][col] and K_map[row][col] == 1:
                    group = []
                    dfs(row, col, group)
                    groups.append(group)

        # Sort groups by size in descending order
        groups.sort(key=lambda g: len(g), reverse=True)
        return groups

    def print_K_map(K_map):
        for row in K_map:
            print(" ".join(map(str, row)))
    '''
    groups_of_ones = find_groups_of_ones(k_map)

    print("\nGroups of Ones:")
    for group in groups_of_ones:
        print(group)
    '''