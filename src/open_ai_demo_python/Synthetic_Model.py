from gen_tree import gen_tree, cell, block, table, sheet
import pandas as pd
from SB_ID import sb_id
from ST_ID import st_id
from chunker import chunk_sheet
from annotator import annotate_cells_ai
from Multi_DOF_comparison import multi_dof_comparison

#the top level object which can manipulate and compare spreadsheets
class synthetic_model:
    def __init__(self, format_json = None, gen_tree = None, training_workbook = None, training_files = None, raw_instances = [], instances = []): #workbook is a dict of names and csv data
        self.raw_instances = [raw_instances] if not isinstance(instances, list) else instances
        self.instances = [instances] if not isinstance(instances, list) else instances
        #if an existing data format is passed in
        if gen_tree or format_json:
            self.tree = gen_tree.from_json(format_json) if format_json else gen_tree
            self.populate()

        #if a set of training file(s) are passed in
        if training_files:
            #if only an example file set passed in
            if isinstance(training_files, list) or isinstance(training_workbook, list) or self.tree:
                self.multi_doc_analyze(new_files=training_files, new_data=training_workbook)
            else:
                #if a single file passed in
                self.get_sheets(filename= training_files, workbook = training_workbook)
        
        #if output instances
        if instances:
            for instance in instances:
                self.populate(instance)

    def get_sheets(self, filename= None, workbook=None):
        if filename:
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
        elif workbook:
            sheets = workbook

        self.analyze_file(sheets)
        return self.tree
    
    def multi_doc_analyze(self, new_files= None, new_data=None):
        #take in multiple workbooks
        #make a tree for each
        #run the tree comparison algorithm
        trees = [self.tree] if self.tree else []
        for file in new_files, new_data:
            sheets = self.get_sheets(file)
            trees.append(gen_tree(sheets=sheets))
        self.tree = multi_dof_comparison(trees)

    def analyze_file(self, sheets: dict):
        #for each tree run the full algorithm
        sheets_list = {}
        for name, Sheet in sheets.items():
            sheets_list.update(chunk_sheet(Sheet, name=name))
            print(f"Sheet: {name}")
        SB_sheets = sb_id(annotate_cells_ai(sheets_list))
        print("Blocked Sheet:")
        print(SB_sheets.to_clean_json())
        print("Tabled Sheet:")
        ST_sheets = st_id(SB_sheets)
        print(ST_sheets.to_json())

        #rest of algorithm
        
        cur_tree = ST_sheets
        return cur_tree

    def populate(self, notebook=None):
        if notebook:
            for name, Sheet in self.tree.sheets.items():
                if name in notebook.keys():
                    Sheet.populate(notebook[name])
        
        self.instances.append(self.tree.to_clean_json())
        
        return self.instances[-1]



def initialize_and_populate_gen_tree():
    # Define cell data for label and data blocks
    label_blocks = [
        block(annotation_type="LABEL", cells=[cell((2, 1), "Date", "LABEL"),
                                              cell((3, 1), "Time", "LABEL"),
                                              cell((4, 1), "Country", "LABEL")]),
        block(annotation_type="LABEL", cells=[cell((1, 2), "George Costanza", "LABEL"),
                                              cell((1, 3), "Bill Jeofry", "LABEL"),
                                              cell((1, 4), "Harper Giorgo", "LABEL")])
    ]
    data_blocks = [
        block(annotation_type = "DATA", cells=[
            cell((2, 2), "10/12/2023", "DATA"), cell((2, 3), "10:15", "DATA"), cell((2, 4), "USA", "DATA"), 
            cell((3, 2), "09/01/2002", "DATA"), cell((3, 3), "14:30", "DATA"), cell((3, 4), "UK", "DATA"), 
            cell((4, 2), "11/22/1963", "DATA"), cell((4, 3), "13:45", "DATA"), cell((4, 4), "Canada", "DATA")
        ])
    ]
    # Create tree
    return gen_tree(sheets=[sheet(name='Sheet1', tables=[table(l0=label_blocks[1],t0=label_blocks[0], data_block=data_blocks[0])])])
