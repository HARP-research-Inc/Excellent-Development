import pytest
import json
from src.python.cell import Cell as cell
from src.python.block import Block as block
from src.python.table import Table as table
from src.python.sheet import Sheet as sheet
from src.python.gen_tree import Gen_Tree as gen_tree

# Test cases for the Cell class
def test_valid_cell_creation():
    c = cell((1, 1), value="test", annotation="DATA")
    assert c.value == "test", "Failed to assign cell value correctly"
    assert c.annotation == "DATA", "Failed to assign cell annotation correctly"
    assert c.block_type == "DATA", "Failed to assign block type correctly"
    assert c.coord == (1,1), "Failed to assign cell coordinates correctly"

def test_invalid_cell_creation():
    with pytest.raises(ValueError, match="Invalid Cell coordinate: expected tuple or 'A1' format, got"):
        c = cell(1234, value="test", annotation="DATA")
    with pytest.raises(ValueError, match="Invalid Excel coordinate, expected 'A1' format, got"):
        c = cell("ZZZ", value="test", annotation="DATA")

# Test cases for the Block class
def test_get_csv_single_data_block():
    # Create cell objects
    cells = [cell((1,1), 'data11', annotation="DATA"), cell((1,2), 'data12', annotation="DATA"), cell((2,1), 'data21', annotation="DATA"), cell((2,2), 'data22', annotation="DATA")]
    
    # Create data block
    data_block = block(cells=cells, annotation_type="DATA")
    
    # Create table with the data block
    tbl = table(data_block=data_block)
    
    csv_result = tbl.get_csv()
    expected_result = """[DATA] 'data11', [DATA] 'data21'
[DATA] 'data12', [DATA] 'data22'"""
    
    assert csv_result == expected_result

def test_get_csv_with_label_blocks():
    # Create cell objects
    data_cells = [cell((1,2), 'data12', annotation="DATA"), cell((2,2), 'data22', annotation="DATA"), cell((1,3), 'data13', annotation="DATA"), cell((2,3), 'data23', annotation="DATA")]
    label_cells_l0 = [cell((1,1), 'label11', annotation="LABEL"), cell((2,1), 'label21', annotation="LABEL")]
    
    # Create blocks
    data_block = block(data_cells, annotation_type="DATA")
    label_block_l0 = block(label_cells_l0, annotation_type="LABEL")
    
    # Create table with the data block and label blocks
    tbl = table(data_block=data_block, l0=label_block_l0)
    
    csv_result = tbl.get_csv()
    expected_result = """[LABEL] 'label11', [LABEL] 'label21'\n[DATA] 'data12', [DATA] 'data22'\n[DATA] 'data13', [DATA] 'data23'"""
    
    assert csv_result == expected_result

def test_valid_block_creation():
    c1 = cell((1, 1), value="test", annotation="DATA")
    c2 = cell((1, 2), value="test2", annotation="DATA")
    b = block([c1, c2])
    assert b.cells == [c1, c2], "Failed to create block with cells"
    assert b.corners == ((1,1), (1,2)), "Failed to determine block corners correctly"
    assert b.size == (1, 2), "Failed to determine block size correctly"
    assert b.annotation_type == "DATA", "Failed to assign block annotation type correctly"

@pytest.mark.dependency(depends=["test_gen_tree_init_with_sheets"])
def test_gen_tree_init_with_json(mock_sheets):
    json_data = [sheet.to_json() for sheet in mock_sheets]
    json_str = json.dumps(json_data)
    gen_tree_obj = gen_tree(json_data=json_str)
    assert gen_tree_obj.data == json_data
    # Assert that the sheets in gen_tree_obj are correct by comparing their JSON representations.
    assert [json.loads(json.dumps(sheet_dict)) for sheet_dict in gen_tree_obj.data] == json_data


def test_empty_block_creation():
    with pytest.raises(ValueError, match="Invalid block size, need at least one cell"):
        b = block([])

def test_inconsistent_block_creation():
    c1 = cell((1, 1), value="test", annotation="DATA")
    c2 = cell((1, 2), value="test2", annotation="LABEL")
    with pytest.raises(ValueError, match="Inconsistent block type, expecting type DATA, found cell with LABEL"):
        b = block([c1, c2])

def test_csv_format():
    c1 = cell((1, 1), value="test", annotation="DATA")
    c2 = cell((1, 2), value="test2", annotation="DATA")
    b = block([c1, c2])
    expected_csv = "1,1,test,DATA\n1,2,test2,DATA"
    assert b.csv_data == expected_csv, "Failed to format CSV data correctly"

def test_block_relative_position():
    c1 = cell((1, 1), value="test", annotation="DATA")
    c2 = cell((1, 2), value="test2", annotation="DATA")
    b = block([c1, c2])
    relative_position = b.get_relative_position((2,2))
    assert relative_position == (-1,-1), "Failed to get correct relative position for block"

@pytest.fixture
def mock_sheets():
    # A function to generate some mock sheets for testing.
    c1 = cell((1, 1), value="1")
    c2 = cell((1, 2), value="2")
    b1 = block([c1, c2])
    t1 = table(expected_position=(0, 0), data_block=b1)
    s1 = sheet("sheet1", [t1])
    return [s1]

@pytest.mark.dependency()
def test_cell_to_json():
    Cell = cell(location=(1,1), value="Value", annotation="ANNOTATION")
    cell_json = Cell.to_json()
    expected_cell_json = {'coord': (1, 1), "value": "Value", "annotation": "ANNOTATION"}

    assert cell_json == expected_cell_json, "Failed to correctly convert cell to JSON"

@pytest.mark.dependency(depends=["test_cell_to_json"])
def test_valid_block_to_json():
    c1 = cell((1, 1), value="test", annotation="DATA")
    c2 = cell((1, 2), value="test2", annotation="DATA")
    b = block([c1, c2])
    json_data = b.to_json()
    expected_json = {
        "start": "(1, 1)",
        "end": "(1, 2)",
        "cells": {
            "(1, 1)": {"value": "test", "annotation": "DATA"},
            "(1, 2)": {"value": "test2", "annotation": "DATA"}
        },
        "size": "(1, 2)",
    }
    assert json_data == expected_json, "Failed to convert block to JSON correctly"

@pytest.mark.dependency(depends=["test_valid_block_to_json"])
def test_valid_table_to_json():
    c1 = cell((1, 1), value="test", annotation="DATA")
    c2 = cell((1, 2), value="test2", annotation="DATA")
    b = block([c1, c2])
    t = table(data_block=b)
    json_data = t.to_json()
    expected_json = {
        "data_block": {
            "start": "(1, 1)",
            "end": "(1, 2)",
            "cells": {
                "(1, 1)": {"value": "test", "annotation": "DATA"},
                "(1, 2)": {"value": "test2", "annotation": "DATA"}
            },
            "size": "(1, 2)"
        },
        "label_blocks": {
            "same_height": {"l0": None, "l1": None, "r0": None, "r1": None},
            "same_width": {"t0": None, "t1": None, "b0": None, "b1": None}
        },
        "subtables": [],
        "free_blocks": {"LABEL": [], "DATA": []},
        "size": "(1, 2)",
        "start": "(1, 1)",
    }
    assert json_data == expected_json, "Failed to convert table to JSON correctly"

#@pytest.mark.dependency(depends=["test_valid_table_to_json"])
def test_gen_tree_to_json(mock_sheets):
    gen_tree_obj = gen_tree(mock_sheets)
    expected_json = json.dumps([sheet.to_json() for sheet in mock_sheets])
    expected_json = expected_json.replace("\"", "'")
    print([gen_tree_obj.to_json()], "\n\n This is exp json -->\n",expected_json)
    assert gen_tree_obj.to_json() == expected_json

# Test cases for the table class
#@pytest.mark.dependency(depends=["test_gen_tree_to_json"])
def test_cell_from_json():
    # Arrange
    original_cell = cell(location="A1", value="test", annotation="DATA")
    cell_json = original_cell.to_json()

    # Act
    final_cell = cell.from_json(cell, cell_json,"A1")

    # Assert
    assert original_cell.value == final_cell.value, f"Failed to correctly convert cell value from JSON, expected: {original_cell.to_json()}, got {final_cell.to_json()}"
    assert original_cell.annotation == final_cell.annotation, "Failed to correctly convert cell annotation from JSON"
    assert original_cell.block_type == final_cell.block_type, "Failed to correctly convert cell block type from JSON"
    assert original_cell.coord == final_cell.coord, "Failed to correctly convert cell coordinates from JSON"

#@pytest.mark.dependency(depends=["test_cell_from_json"])
def test_block_from_json():
    # Arrange
    cells = [cell(location=(1,1), value="A1", annotation="DATA"), cell(location=(1,2), value="A2", annotation="DATA")]
    original_block = block(cells)
    block_json = original_block.to_json()

    # Act
    final_block = block.from_json(block_json)

    # Assert
    assert len(original_block.cells) == len(final_block.cells), f"Failed to correctly convert block cells from JSON, expected {[cell.to_json() for cell in original_block.cells]} got {[cell.to_json() for cell in final_block.cells]}"
    assert original_block.annotation_type == final_block.annotation_type, "Failed to correctly convert block annotation type from JSON"
    assert original_block.corners == final_block.corners, "Failed to correctly convert block corners from JSON"

#@pytest.mark.dependency(depends=["test_block_from_json"])
def test_table_from_json():
    # Arrange
    Cells = [cell(location=(1,1), value="A1", annotation="DATA"), cell(location=(1,2), value="A2", annotation="DATA")]
    Block = block(Cells)
    original_table = table(expected_position=(0,0), data_block=Block)
    table_json = original_table.to_json()

    # Act
    final_table = table.from_json(table_json)

    # Assert
    assert original_table.data_block.to_json() == final_table.data_block.to_json(), "Failed to correctly convert table data block from JSON"
    assert original_table.expected_size == final_table.expected_size, f"Failed to correctly convert table expected size from JSON, expected {original_table.to_json()} but got {final_table.to_json()}"
    assert original_table.expected_position == final_table.expected_position, "Failed to correctly convert table expected position from JSON"

#@pytest.mark.dependency(depends=["test_table_from_json"])
def test_table_relative_position():
    c1 = cell((1, 1), value="test", annotation="DATA")
    c2 = cell((1, 2), value="test2", annotation="DATA")
    b = block([c1, c2])
    t = table(data_block=b)
    relative_position = t.get_relative_position((2,2))
    assert relative_position == (-1,-1), "Failed to get correct relative position for table"

#@pytest.mark.dependency(depends=["test_table_relative_position"])
def test_gen_tree_init_with_sheets(mock_sheets):
    gen_tree_obj = gen_tree(mock_sheets)
    assert gen_tree_obj.sheets.get('sheet1') == mock_sheets[0]
    assert [gen_tree_obj.data] == [sheet.to_json() for sheet in mock_sheets]

# @pytest.mark.dependency(depends=["test_gen_tree_init_with_sheets"])
def test_gen_tree_init_with_json(mock_sheets):
    json_data = [sheet.to_json() for sheet in mock_sheets]
    json_str = json.dumps(json_data)
    gen_tree_obj = gen_tree(json_data=json_str)
    #assert gen_tree_obj.data == json_data
    # Assert that the sheets in gen_tree_obj are correct by comparing their JSON representations.
    assert [json.loads(json.dumps(sheet_dict)) for sheet_dict in gen_tree_obj.data] == json_data

# @pytest.mark.dependency(depends=["test_gen_tree_init_with_json"])
def test_gen_tree_get_unenclosed_tables(mock_sheets):
    gen_tree_obj = gen_tree(mock_sheets)
    unenclosed_tables = gen_tree_obj.get_unenclosed_tables()
    # Since the mock_sheets fixture only contains enclosed tables, the result should be empty.
    print("sand", unenclosed_tables)
    assert unenclosed_tables == []

# @pytest.mark.dependency(depends=["test_gen_tree_get_unenclosed_tables"])
def test_gen_tree_get_prime_width_tables(mock_sheets):
    gen_tree_obj = gen_tree(mock_sheets)
    prime_width_tables = gen_tree_obj.get_prime_width_tables()
    # Since the mock_sheets fixture only contains tables of size (1, 2), the result should be empty.
    assert prime_width_tables == []