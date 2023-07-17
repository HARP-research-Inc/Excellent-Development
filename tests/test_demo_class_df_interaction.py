import pytest
import pandas as pd
from src.open_ai_demo_python.gen_tree import cell, block, table

# Create a dataframe for testing
df = pd.DataFrame({
    'A': ['1', '2', '3', '4', '5'],
    'B': ['a', 'b', 'c', 'd', 'e'],
    'C': ['alpha', 'beta', 'gamma', 'delta', 'epsilon']
})

# Define cells
cell_1 = cell(location=(1,1), value='1', annotation="DATA")
cell_2 = cell(location=(1,2), value='a', annotation="LABEL")
cell_3 = cell(location=(1,3), value='alpha', annotation="LABEL")

# Define blocks
data_block = block(cells=[cell_1])
label_block_1 = block(cells=[cell_2])
label_block_2 = block(cells=[cell_3])

# Define table
tbl = table(expected_position=(1,1), free_labels=[label_block_1, label_block_2], free_data=[data_block])

def test_to_dataframe_data_block():
    df = tbl.to_dataframe()

    assert df.at[0, 'a'] == 1, "Failed to correctly populate dataframe with data block values"

def test_to_dataframe_label_block():
    df = tbl.to_dataframe()

    assert 'a' in df.columns, "Failed to correctly populate dataframe with label block values"
    assert df.columns[0] == 'a', "Failed to correctly set label block values as column names"

@pytest.mark.dependency(depends=['test_to_dataframe_label_block', 'test_to_dataframe_data_block'])
def test_to_dataframe_empty_data_block():
    # Modify data block to have no cells
    tbl.data_block.cells = []

    df = tbl.to_dataframe()

    assert df.empty, "Failed to handle empty data block"

@pytest.mark.dependency(depends=['test_to_dataframe_label_block', 'test_to_dataframe_data_block'])
def test_to_dataframe_empty_label_block():
    # Modify label blocks to have no cells
    tbl.free_labels = []

    df = tbl.to_dataframe()

    assert df.columns.empty, "Failed to handle empty label blocks"
    
@pytest.mark.dependency(depends=['test_to_dataframe_empty_label_block', 'test_to_dataframe_empty_data_block', 'test_to_dataframe_label_block', 'test_to_dataframe_data_block'])
def test_check_df_ep_valid_input():
    result = tbl.check_df_ep(df)
    print(tbl.to_dataframe())
    print(df)
    assert result == True, "Failed to correctly verify dataframe for valid input"

@pytest.mark.dependency(depends=['test_to_dataframe_empty_label_block', 'test_to_dataframe_empty_data_block', 'test_to_dataframe_label_block', 'test_to_dataframe_data_block'])
def test_check_df_ep_invalid_input():
    # Modify dataframe
    df.at[0, 'A'] = 100

    result = tbl.check_df_ep(df)
    assert result == False, "Failed to detect invalid input in dataframe"

@pytest.mark.dependency(depends=['test_to_dataframe_empty_label_block', 'test_to_dataframe_empty_data_block', 'test_to_dataframe_label_block', 'test_to_dataframe_data_block'])
def test_check_df_ep_free_labels():
    print(tbl.to_clean_json())
    # Modify dataframe
    df.at[0, 'B'] = 'z'

    result = tbl.check_df_ep(df)
    print(tbl.to_clean_json())
    assert result == {'(0,1)': 'z'}, "Failed to detect changes in free label blocks"

@pytest.mark.dependency(depends=['test_check_df_ep_free_labels','test_to_dataframe_empty_label_block', 'test_to_dataframe_empty_data_block', 'test_to_dataframe_label_block', 'test_to_dataframe_data_block'])
def test_check_df_ep_update_free_data():
    # Modify dataframe
    df.at[0, 'A'] = 10

    result = tbl.check_df_ep(df)
    assert result == {'(0,0)': 10}, "Failed to update free data blocks when free label blocks are modified"
