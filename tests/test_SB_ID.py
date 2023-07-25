
import json
from collections import defaultdict
import pytest
from SB_ID import extract_number, extract_column
from SB_ID import generate_solid_blocks, merge_blocks

# python3.9 -m pytest

def test_01_extract_number():
    assert extract_number('A1') == 1
    assert extract_number('B100') == 100


def test_02_extract_column():
    assert extract_column('A1') == 'A'
    assert extract_column('AA23') == 'AA'


@pytest.mark.dependency()
def test_03_generate_solid_blocks():
    sheet1 = {
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "B1": {"annotation": "DATA"},
            "A2": {"annotation": "LABEL"},
            "B2": {"annotation": "LABEL"},
        }
    }
    blocks = generate_solid_blocks(sheet1)
    assert len(
        blocks['DATA']) == 1, f"a: Failed to generate solid blocks, expected 1 DATA block, got {len(blocks['DATA'])}"
    assert len(
        blocks['LABEL']) == 1, f"b: Failed to generate solid blocks, expected 1 LABEL block, got {len(blocks['LABEL'])}"
    # Prepare a mock sheet with no annotations
    sheet = {
        "Sheet number": 1,
        "Annotations": {}
    }

    # Generate blocks
    blocks = generate_solid_blocks(sheet)

    # Verify the result
    assert len(blocks) == 0, "c: Failed to handle an empty sheet"

    # Prepare a mock sheet with a single block of the same annotation
    sheet = {
        "Sheet number": 1,
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "A2": {"annotation": "DATA"},
            "A3": {"annotation": "DATA"},
        }
    }

    # Generate blocks
    blocks = generate_solid_blocks(sheet)

    # Verify the result
    expected_num_blocks = 1
    assert len(blocks['DATA']) == expected_num_blocks, f"d: Failed to generate a single block, expected {expected_num_blocks} block, got {len(blocks['DATA'])}"

    # Prepare a mock sheet with multiple blocks of different annotations
    sheet = {
        "Sheet number": 1,
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "A2": {"annotation": "DATA"},
            "B1": {"annotation": "LABEL"},
            "C1": {"annotation": "DATA"},
            "C2": {"annotation": "DATA"},
            "D1": {"annotation": "LABEL"},
            "D2": {"annotation": "LABEL"},
            "D3": {"annotation": "LABEL"},
        }
    }

    # Generate blocks
    blocks = generate_solid_blocks(sheet)

    # Verify the result
    expected_num_data_blocks = 2
    assert len(blocks['DATA']) == expected_num_data_blocks, f"f: Failed to generate multiple data blocks, expected {expected_num_data_blocks} blocks, got {len(blocks['DATA'])}"
    expected_num_label_blocks = 2
    assert len(blocks['LABEL']) == expected_num_label_blocks, f"g: Failed to generate multiple label blocks, expected {expected_num_label_blocks} blocks, got {len(blocks['LABEL'])}"

    # Prepare a mock sheet with mixed blocks of the same annotation
    sheet = {
        "Sheet number": 1,
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "A2": {"annotation": "DATA"},
            "A4": {"annotation": "DATA"},
            "B1": {"annotation": "DATA"},
            "C1": {"annotation": "DATA"},
            "C2": {"annotation": "DATA"},
        }
    }

    # Generate blocks
    blocks = generate_solid_blocks(sheet)

    # Verify the result
    expected_num_data_blocks = 3
    assert len(blocks['DATA']) == expected_num_data_blocks, f"h: Failed to generate mixed data blocks, expected {expected_num_data_blocks} blocks, got {len(blocks['DATA'])}"


@pytest.mark.dependency(depends=["test_03_generate_solid_blocks"])
def test_04_non_sequential_cells():
    # Prepare a mock sheet with non-sequential cells
    sheet = {
        "Sheet number": 1,
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "A3": {"annotation": "DATA"},
            "A5": {"annotation": "DATA"},
        }
    }

    # Generate and merge blocks
    blocks = generate_solid_blocks(sheet)
    merged_blocks = merge_blocks(blocks)

    # Verify the result
    assert len(
        merged_blocks['DATA']) == 3, f"a: Failed to handle non-sequential cells, expected 3 cells, got {len(merged_blocks['DATA'])}"

# Test the case of varied block lengths
@pytest.mark.dependency(depends=["test_03_generate_solid_blocks"])
def test_05_varied_block_lengths_columns():
    # Prepare a mock sheet with blocks of different lengths in columns
    sheet = {
        "Sheet number": 1,
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "A2": {"annotation": "DATA"},
            "B1": {"annotation": "DATA"},
            "C1": {"annotation": "DATA"},
            "C2": {"annotation": "DATA"},
            "D1": {"annotation": "DATA"},
            "D2": {"annotation": "DATA"},
            "D3": {"annotation": "DATA"},
        }
    }

    # Generate and merge blocks
    blocks = generate_solid_blocks(sheet)
    merged_blocks = merge_blocks(blocks)

    # Verify the result
    expected_num_blocks = 4
    assert len(merged_blocks['DATA']) == expected_num_blocks, f"a: Failed to handle blocks of varied lengths in columns, expected {expected_num_blocks} blocks, got {len(merged_blocks['DATA'])}"

@pytest.mark.dependency(depends=["test_03_generate_solid_blocks"])
def test_06_varied_block_lengths_rows():
    # Prepare a mock sheet with blocks of different lengths in rows
    sheet = {
        "Sheet number": 1,
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "A2": {"annotation": "DATA"},
            "A3": {"annotation": "DATA"},
            "B1": {"annotation": "DATA"},
            "C1": {"annotation": "DATA"},
            "C2": {"annotation": "DATA"},
        }
    }

    # Generate and merge blocks
    blocks = generate_solid_blocks(sheet)
    merged_blocks = merge_blocks(blocks)

    # Verify the result
    expected_num_blocks = 3
    assert len(merged_blocks['DATA']) == expected_num_blocks, f"a: Failed to handle blocks of varied lengths in rows, expected {expected_num_blocks} blocks, got {len(merged_blocks['DATA'])}"

@pytest.mark.dependency(depends=["test_05_varied_block_lengths_columns", "test_06_varied_block_lengths_rows"])
def test_07_varied_block_lengths_both():
    # Prepare a mock sheet with blocks of different lengths in both columns and rows
    sheet = {
        "Sheet number": 1,
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "A2": {"annotation": "DATA"},
            "B1": {"annotation": "DATA"},
            "C1": {"annotation": "DATA"},
            "C2": {"annotation": "DATA"},
            "D1": {"annotation": "DATA"},
            "D2": {"annotation": "DATA"},
            "D3": {"annotation": "DATA"},
            "E3": {"annotation": "DATA"},
            "F3": {"annotation": "DATA"},
        }
    }

    # Generate and merge blocks
    blocks = generate_solid_blocks(sheet)
    merged_blocks = merge_blocks(blocks)

    # Verify the result
    expected_num_blocks = 5
    assert len(merged_blocks['DATA']) == expected_num_blocks, f"a: Failed to handle blocks of varied lengths in columns and rows, expected {expected_num_blocks} blocks, got {len(merged_blocks['DATA'])}"

# Test the case of special characters in cell names


@pytest.mark.dependency(depends=["test_04_non_sequential_cells",
                        "test_07_varied_block_lengths_both"])
def test_08_special_characters():
    # Prepare a mock sheet with special characters in cell names
    sheet = {
        "Sheet number": 1,
        "Annotations": {
            "A!1": {"annotation": "DATA"},
            "A#2": {"annotation": "DATA"},
            "B@1": {"annotation": "DATA"},
        }
    }

    # Generate and merge blocks
    blocks = generate_solid_blocks(sheet)
    merged_blocks = merge_blocks(blocks)

    # Verify the result
    assert len(
        merged_blocks['DATA']) == 2, f"a: Failed to handle special characters in cell names, expected 3 cells, got {len(merged_blocks['DATA'])}"

# Test the case of empty sheets


def test_09_empty_sheet():
    # Prepare a mock empty sheet
    sheet = {
        "Sheet number": 1,
        "Annotations": {}
    }

    # Generate and merge blocks
    blocks = generate_solid_blocks(sheet)
    merged_blocks = merge_blocks(blocks)

    # Verify the result
    assert len(merged_blocks) == 0, "a: Failed to handle empty sheets"


def test_10_merge_blocks():
    sheet1 = {
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "B1": {"annotation": "DATA"},
            "A2": {"annotation": "LABEL"},
            "B2": {"annotation": "LABEL"},
        }
    }
    blocks = generate_solid_blocks(sheet1)
    merged_blocks = merge_blocks(blocks)

    # Assert the length of merged_blocks['DATA']
    expected_data_length = 1
    assert len(
        merged_blocks['DATA']) == expected_data_length, f"a: Expected {expected_data_length} merged DATA block(s), but got {len(merged_blocks['DATA'])}"

    # Assert the length of merged_blocks['LABEL']
    expected_LABEL_length = 1
    assert len(
        merged_blocks['LABEL']) == expected_LABEL_length, f"b: Expected {expected_LABEL_length} merged LABEL block(s), but got {len(merged_blocks['LABEL'])}"


def test_11_empty_input():
    blocks = generate_solid_blocks({"Annotations": {}})
    assert blocks == defaultdict(list)


def test_12_output(tmp_path):
    output_file = tmp_path / "blocks_output.json"
    sheet2 = {
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "B1": {"annotation": "DATA"},
            "A2": {"annotation": "LABEL"},
            "B2": {"annotation": "LABEL"},
        }
    }
    blocks = generate_solid_blocks(sheet2)
    merged_blocks = merge_blocks(blocks)
    with open(output_file, "w") as outfile:
        json.dump(merged_blocks, outfile, indent=4)
    assert output_file.exists()