from src.python.structures.cell import Cell as cell
from src.python.structures.block import Block as block
from src.python.structures.table import Table as table
from src.python.structures.sheet import Sheet as sheet
from src.python.structures.gen_tree import Gen_Tree as gen_tree
from src.python.ST_ID import st_id
from src.python.SB_ID import sb_id
from src.python.Synthetic_Model import synthetic_model
from src.python.chunker import chunk_sheet
from src.python.annotator import annotate_cells_ai
import pandas as pd

def test_st_id():
    # Prepare input data
    # Prepare input data
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
    input_tree = gen_tree(sheets=[sheet(name="Sheet 1", free_labels=label_blocks, free_data=data_blocks)])

    # Call the function with the prepared input
    output_tree = st_id(input_tree)

 

    tables = [
        table(
            expected_position=(1,1),
            free_labels=[],
            free_data=[],
            subtables=[],
            t0=label_blocks[0],
            l0=label_blocks[1],
            data_block=data_blocks[0]
        )
    ]
    expected_output_tree = gen_tree(sheets=[sheet(name="Sheet 1", tables=tables)])

    # Assert that the function output is as expected
    assert output_tree.to_json() == expected_output_tree.to_json(), f"expected {expected_output_tree.to_clean_json()}, got {output_tree.to_clean_json()}"

def test_to_dataframe():
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
    # Create table
    table_instance = table(l0=label_blocks[1],t0=label_blocks[0], data_block=data_blocks[0])

    # Call to_dataframe
    df = table_instance.to_dataframe()

    # Expected dataframe
    expected_df = pd.DataFrame({
        'George Costanza': ['10/12/2023', '10:15', 'USA'],
        'Bill Jeofry': ['09/01/2002', '14:30', 'UK'],
        'Harper Giorgo': ['11/22/1963', '13:45', 'Canada']
    }, index=['Date', 'Time', 'Country'])

    print("expected_df:")
    print(expected_df)
    print("df:")
    print(df)
    # Assert that the dataframes match
    assert df.equals(expected_df)

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

def test_synthetic_model():
    # Initialize gen_tree
    # gen_tree is assumed to be initialized and populated elsewhere
    gen_tree = initialize_and_populate_gen_tree()

    # Create synthetic_model
    synthetic_model_instance = synthetic_model(gen_tree)

    # Prepare csv data for testing
    csv_data = ',,,\n,A,B,C\na,1,2,3\nb,4,5,6\nc,7,8,9'

    # Call populate with csv data
    synthetic_model_instance.populate(csv_data=csv_data, name='Sheet1')

    # Prepare expected dataframe
    expected_df = pd.DataFrame({'A': ['1', '4', '7'], 'B': ['2', '5', '8'], 'C': ['3', '6', '9']})

    # Retrieve the populated dataframe
    populated_df = list(synthetic_model_instance.sheets['Sheet1'].values())[0]

    print(f"Expected {expected_df}, but got {populated_df}")
    # Assert that the populated dataframe matches the expected dataframe
    assert populated_df.equals(expected_df), f"Expected {expected_df}, but got {populated_df}"

    # Convert the synthetic model to JSON
    json_data = synthetic_model_instance.to_json()

    # Check that the JSON data is not empty and that it has the right structure
    assert json_data, "JSON data is empty"
    assert 'Sheet1' in json_data, "Sheet1 is not in JSON data"
    assert isinstance(json_data['Sheet1'], list), "Sheet1 data is not a list"
    assert len(json_data['Sheet1']) > 0, "Sheet1 data list is empty"
    assert isinstance(json_data['Sheet1'][0], str), "DataFrame JSON data is not a string"
    print("All tests passed.")

    #testfunct()
    #test_synthetic_model()

    csv_test_1 = """,Product,Price,Quantity,Category
    Label 1,Apple,0.99,10, 14
    Label 2,Banana,0.59,8,23
    Label 3,Milk,2.99,5,34
    Label 4,Bread,1.99,3,56"""
    sheets_list = {}
    sheets_list.update(chunk_sheet(csv_test_1, name="Amazon Sheet"))
    print(f"Sheet: {sheets_list}")
    SB_sheets = sb_id(annotate_cells_ai(sheets_list))
    print("Blocked Sheet:")
    print(SB_sheets.to_clean_json())
    print("Tabled Sheet:")
    ST_sheets = st_id(SB_sheets)
    print(ST_sheets.to_json())
    print("Json Output:")
    syn_model = synthetic_model(ST_sheets)
    print(syn_model.to_json())
    print(list(syn_model.sheets['Amazon Sheet'].values())[0])
