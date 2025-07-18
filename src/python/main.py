from structures.cell import Cell as cell
from structures.block import Block as block
from structures.table import Table as table
from structures.sheet import Sheet as sheet
from structures.gen_tree import Gen_Tree as gen_tree
import json
from SB_ID import sb_id
from ST_ID import st_id
from ST_ID2 import st_id2
from LB_ID_LABEL import lb_id_label
from LB_ID_AB import lb_id_ab
from LB_ID_BB import lb_id_bb
from LB_ID_CB import lb_id_cb
from Pattern_Splitting import pattern_splitting
from Recursive_Table_ID import recursive_table_id
from Template_Extraction import template_extraction
from Synthetic_Model import synthetic_model
from Multi_DOF_comparison import multi_dof_comparison
from chunker import chunk_sheet
from annotator import annotate_cells_ai
import pandas as pd


def analyze_file(filename = None):
    # Determine file type
    file_type = filename.split('.')[-1]

    if file_type in ['xlsx', 'xls']:
        # Use pandas to read Excel file and convert each sheet into csv format
        xls = pd.ExcelFile(filename)
        sheets = {sheet_name: xls.parse(sheet_name).to_csv() for sheet_name in xls.sheet_names}
    elif file_type == 'csv':
        # If the file is already a csv, just read it
        with open(filename, 'r') as f:
            sheets = {filename: f.read()}
    else:
        raise ValueError('Unsupported file type: {}'.format(file_type))

    sheets_list = {}
    for name, csv in sheets.items():
        sheets_list.update(chunk_sheet(csv_data=csv, name=name))
    
    SB_sheets = sb_id(annotate_cells_ai(sheets_list), name)

    tree = gen_tree(sheets=SB_sheets)
    st_id(tree)
    #st_id2(tree)
    #lb_id_label(tree)
    #lb_id_ab(tree)
    #lb_id_bb(tree)
    #lb_id_cb(tree)
    #pattern_splitting(tree)
    #recursive_table_id(tree)
    #template_extraction(tree)

    return tree

def main(training_instances=None, format_json=None, instances=None, print_instances=False):
    all_instances = training_instances + instances if training_instances and instances else []
    instance_jsons = []
    model = None

    if not format_json and training_instances:
        files = training_instances
        trees = []
        for file in files:
            trees.append(analyze_file(file))
        generalized_tree = multi_dof_comparison(trees)
        model = synthetic_model(tree=generalized_tree) 
        format_json = model.to_json()
        
    if format_json and all_instances:
        model = synthetic_model(format_json=format_json) 
    elif not all_instances:
        raise ValueError("No instances to organize")
    elif not format_json and not training_instances:
        raise ValueError("No way to train model")

    instance_jsons = model.sort(all_instances)

    if print_instances:
        for json_instance in instance_jsons:
            print(json_instance)
    else:
        with open('instances.json', 'w') as f:
            json.dump(instance_jsons, f)

#main()

csv_test_1 = """, "Date", "Time", "Country"
"George Costanza", "10/12/2023","10:15", "USA"
"Bill Jeofry", "09/01/2002", "14:30", "UK"
"Harper Giorgo", "11/22/1963", "13:45", "Canada"
, "Book Title", "Author"
"George Costanza", "The Art of War", "Sun Tzu"
, "Book Title", "Author"
"Harper Giorgo", "1984", "George Orwell"
"""
'''csv_test_1 = """, "Date", "Time", "Country"
"George Costanza", "10/12/2023","10:15", "USA"
"Bill Jeofry", "09/01/2002", "14:30", "UK"
"Harper Giorgo", "11/22/1963", "13:45", "Canada"
"""'''
sheets_list = {}
sheets_list.update(chunk_sheet(csv_test_1, name="Amazon Sheet"))

SB_sheets = sb_id(annotate_cells_ai(sheets_list))
print(SB_sheets)
