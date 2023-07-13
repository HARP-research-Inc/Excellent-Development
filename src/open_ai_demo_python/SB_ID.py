from gen_tree import cell
from io import StringIO
import csv
from gen_tree import cell, sheet, block
from tabulate import tabulate

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
    print(cur_sheet.to_json())
    #make a csv of all cells
    #ask for a json of 


# Create some cells for the sheet
cells = [
    cell((1,1), '1', 'LABEL'), 
    cell((1,2), '2', 'LABEL'), 
    cell((2,1), 'A', 'DATA'), 
    cell((2,2), 'B', 'DATA'), 
    cell((2,3), 'C', 'DATA')
]

# Use sb_id function to create sheet and print CSV
sb_id(cells, "Sheet 1")
