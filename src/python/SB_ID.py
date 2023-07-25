import sys
if 'pytest' in sys.modules:
    from src.python.gen_tree import Gen_Tree as gen_tree
    from src.python.cell import Cell as cell
    from src.python.sheet import Sheet as sheet
    from src.python.block import Block as block
   
else:
    from src.python.gen_tree import Gen_Tree as gen_tree
    from src.python.cell import Cell as cell
    from src.python.sheet import Sheet as sheet
    from src.python.block import Block as block
    
from src.python.prompt_interface import prompt_interface
import os
import json

def sb_id(sheets):
    SB_sheets = {}
    for name, cell_dict in sheets.items():
        labels = []
        data = []
        redo_dict = {}
        redo_dict.update(cell_dict)
        for coord, Cell in redo_dict.items():
            if Cell['annotation'] == 'EMPTY':
                continue
            Block = block(cells=[cell(location=coord, value=Cell['value'],annotation=Cell['annotation'])])
            if Block.annotation_type == "LABEL":
                labels.append(Block)
            if Block.annotation_type == "DATA":
                data.append(Block)
        label_cur_sheet = sheet(name=name, free_labels=labels)
        data_cur_sheet = sheet(name=name, free_data=data)
        label_csv = label_cur_sheet.get_csv()
        data_csv = data_cur_sheet.get_csv()
        openai_api_key = os.getenv('openai_api_key')
        label_variables = {"in":{"csv":label_csv},"out":["json"]}
        data_variables = {"in":{"csv":data_csv},"out":["json"]}
        input_structure = "Consolidate the following annotated csv into a json with uninteruppted blocks: {csv}"
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

        json_SB_data = prompt_interface(openai_api_key=openai_api_key, variables=data_variables, input_structure=input_structure, examples=data_examples)['json']
        json_SB_labels = prompt_interface(openai_api_key=openai_api_key, variables=label_variables, input_structure=input_structure, examples=labels_examples)['json']
        SB_sheet = sheet(name=name)
        for Block in json.loads(json_SB_data):
            cells = {}
            for coord, Cell in Block['cells'].items():
                if Cell['annotation'] != "EMPTY":
                    cells[coord]=Cell
            Block['cells']=cells
            new_block = block.from_json(Block)
            if new_block.annotation_type == "DATA":
                SB_sheet.free_data.append(new_block)
        for Block in json.loads(json_SB_labels):
            cells = {}
            for coord, Cell in Block['cells'].items():
                if Cell['annotation'] != "EMPTY":
                    cells[coord]=Cell
            Block['cells']=cells
            new_block = block.from_json(Block)
            if new_block.annotation_type == "LABEL":
                SB_sheet.free_labels.append(new_block)
        SB_sheets[name] = SB_sheet
    SB_tree = gen_tree(sheets = SB_sheets)
    return SB_tree
