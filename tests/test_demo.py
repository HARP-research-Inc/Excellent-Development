import pytest
import src.open_ai_demo_python.gen_tree as gt

# Test cases for the Cell class

def test_valid_cell_creation():
    c = gt.cell((1, 1), value="test", annotation="DATA")
    assert c.value == "test", "Failed to assign gt.cell value correctly"
    assert c.annotation == "DATA", "Failed to assign gt.cell annotation correctly"
    assert c.block_type == "DATA", "Failed to assign block type correctly"
    assert c.coord == (1,1), "Failed to assign gt.cell coordinates correctly"

def test_invalid_cell_creation():
    with pytest.raises(ValueError, match="Invalid Cell coordinate: expected tuple or 'A1' format, got"):
        c = gt.cell(1234, value="test", annotation="DATA")
    with pytest.raises(ValueError, match="Invalid Excel coordinate, expected 'A1' format, got"):
        c = gt.cell("ZZZ", value="test", annotation="DATA")

# Test cases for the Block class

def test_valid_block_creation():
    c1 = gt.cell((1, 1), value="test", annotation="DATA")
    c2 = gt.cell((1, 2), value="test2", annotation="DATA")
    b = gt.block([c1, c2])
    assert b.cells == [c1, c2], "Failed to create block with cells"
    assert b.corners == ((1,1), (1,2)), "Failed to determine block corners correctly"
    assert b.size == (0, 1), "Failed to determine block size correctly"
    assert b.annotation_type == "DATA", "Failed to assign block annotation type correctly"

def test_empty_block_creation():
    with pytest.raises(ValueError, match="Invalid block size, need at least one cell"):
        b = gt.block([])

def test_inconsistent_block_creation():
    c1 = gt.cell((1, 1), value="test", annotation="DATA")
    c2 = gt.cell((1, 2), value="test2", annotation="LABEL")
    with pytest.raises(ValueError, match="Inconsistent block type, expecting type DATA, found cell with LABEL"):
        b = gt.block([c1, c2])

def test_csv_format():
    c1 = gt.cell((1, 1), value="test", annotation="DATA")
    c2 = gt.cell((1, 2), value="test2", annotation="DATA")
    b = gt.block([c1, c2])
    expected_csv = "1,1,test,DATA\n1,2,test2,DATA"
    assert b.csv_data == expected_csv, "Failed to format CSV data correctly"

def test_valid_block_to_json():
    c1 = gt.cell((1, 1), value="test", annotation="DATA")
    c2 = gt.cell((1, 2), value="test2", annotation="DATA")
    b = gt.block([c1, c2])
    json_data = b.to_json()
    expected_json = {
        "start": "(1, 1)",
        "end": "(1, 2)",
        "cells": {
            "(1, 1)": {"value": "test", "annotation": "DATA"},
            "(1, 2)": {"value": "test2", "annotation": "DATA"}
        },
        "size": "(0, 1)"
    }
    assert json_data == expected_json, "Failed to convert block to JSON correctly"

def test_block_relative_position():
    c1 = gt.cell((1, 1), value="test", annotation="DATA")
    c2 = gt.cell((1, 2), value="test2", annotation="DATA")
    b = gt.block([c1, c2])
    relative_position = b.get_relative_position((2,2))
    assert relative_position == (-1,-1), "Failed to get correct relative position for block"

# Test cases for the table class

def test_valid_table_to_json():
    c1 = gt.cell((1, 1), value="test", annotation="DATA")
    c2 = gt.cell((1, 2), value="test2", annotation="DATA")
    b = gt.block([c1, c2])
    t = gt.table(data_block=b)
    json_data = t.to_json()
    expected_json = {
        "data_block": {
            "start": "(1, 1)",
            "end": "(1, 2)",
            "cells": {
                "(1, 1)": {"value": "test", "annotation": "DATA"},
                "(1, 2)": {"value": "test2", "annotation": "DATA"}
            },
            "size": "(0, 1)"
        },
        "label_blocks": {
            "same_height": {"l0": None, "l1": None, "r0": None, "r1": None},
            "same_width": {"t0": None, "t1": None, "b0": None, "b1": None}
        },
        "subtables": [],
        "free_blocks": {"LABEL": [], "DATA": []}
    }
    assert json_data == expected_json, "Failed to convert table to JSON correctly"

def test_table_relative_position():
    c1 = gt.cell((1, 1), value="test", annotation="DATA")
    c2 = gt.cell((1, 2), value="test2", annotation="DATA")
    b = gt.block([c1, c2])
    t = gt.table(data_block=b)
    relative_position = t.get_relative_position((2,2))
    assert relative_position == (-2,-2), "Failed to get correct relative position for table"
