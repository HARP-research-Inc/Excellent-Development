from gen_tree import cell, sheet, block
from prompt_interface import prompt_interface
import os
import json

def sb_id(cells: list[cell], name):
    labels =[]
    data = []
    for Cell in cells:
        Block = block(cells=[Cell])
        if Cell.block_type == "LABEL":
            labels.append(Block)
        if Cell.block_type == "DATA":
            data.append(Block)

    cur_sheet = sheet(free_data=data, free_labels=labels, name=name)
    csv = cur_sheet.get_csv()
    print(csv)
    blocks_string = cur_sheet.to_json().get("free_labels")+cur_sheet.to_json().get("free_data")
    print(blocks_string)
    #make a csv of all cells
    #ask for a json of the solid_blocks all together

    # Usage
    openai_api_key = os.getenv('openai_api_key')
    variables = {"in":{"csv":csv},"out":["json"]}
    input_structure = "Consolidate the following annotated csv into a json with solid blocks: {csv}"
    examples = [
        {
            "user": {"csv": """[LABEL] '1', [DATA] 'A'\n[LABEL] '2', [DATA] 'B'\n[EMPTY] ' ', [DATA] 'C'"""}, 
            "assistant": {"json": """[{"start": "(1, 1)","end": "(1, 2)","cells": {"(1, 1)": {"value": "1", "annotation": "LABEL"},"(1, 2)": {"value": "2","annotation": "LABEL"}},"size": "(1, 2)"},{"start": "(1, 2)","end": "(1, 2)","cells": {"(2, 1)": {"value": "A", "annotation": "DATA"},"(2, 2)": {"value": "B", "annotation": "DATA"},"(2, 3)": {"value": "C", "annotation": "DATA"}, "size": "(1, 1)"}}]"""}
        },
        {
            "user": {"csv": """[LABEL] 'Property Name', [LABEL] 'Property Type', [LABEL] 'Date Acquired'\n[DATA] 'El Ranchero', [DATA] 'Industrial', [DATA] '10/23/2015'\n[DATA] 'The Appartments on the Hudson', [DATA] 'Residential', [DATA] '07/15/2016'"""}, 
            "assistant": {"json": """[{"start": "(1, 1)","end": "(1, 3)","cells": {"(1, 1)": {"value": "Property Name","annotation": "LABEL"},"(1, 2)": {"value": "Property Type","annotation": "LABEL"},"(1, 3)": {"value": "Date Acquired","annotation": "LABEL"}},"size": "(1, 3)"},{"start": "(2, 1)","end": "(3, 3)","cells": {"(2, 1)": {"value": "El Ranchero","annotation": "DATA"},"(2, 2)": {"value": "Industrial","annotation": "DATA"},"(2, 3)": {"value": "10/23/2015","annotation": "DATA"},"(3, 1)": {"value": "The Appartments on the Hudson","annotation": "DATA"},"(3, 2)": {"value": "Residential","annotation": "DATA"},"(3, 3)": {"value": "07/15/2016","annotation": "DATA"}},"size": "(2, 3)"}]"""}
        }
    ]

    json_SB_data = prompt_interface(openai_api_key=openai_api_key, variables=variables, input_structure=input_structure, examples=examples)['json']
    SB_sheet = sheet(name=name)
    print(json_SB_data)
    for Block in json.loads(json_SB_data):
        new_block = block.from_json(Block)
        if new_block.annotation_type == "DATA":
            SB_sheet.free_data.append(new_block)
        elif new_block.annotation_type == "LABEL":
            SB_sheet.free_labels.append(new_block)
        elif new_block.annotation_type != "EMPTY":
            raise ValueError(f"Invalid block type: {new_block.annotation_type}")
    print(SB_sheet)
    return SB_sheet

def testfunction():
    # Create some cells for the sheet
    cells_2 = [
        cell((1,1), 'Name', 'LABEL'),
        cell((2,1), 'Age', 'LABEL'),
        cell((3,1), 'Occupation', 'LABEL'),
        cell((1,2), 'Alice', 'DATA'),
        cell((2,2), '25', 'DATA'),
        cell((3,2), 'Engineer', 'DATA'),
        cell((1,3), 'Bob', 'DATA'),
        cell((2,3), '30', 'DATA'),
        cell((3,3), 'Doctor', 'DATA')
    ]

    # Use sb_id function to create sheet and print CSV
    sb_id(cells_2, "Occupations")
