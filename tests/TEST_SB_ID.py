import json
from collections import defaultdict
import pytest
from src.python.Identification.SB_ID import extract_number, extract_column
from src.python.Identification.SB_ID import generate_solid_blocks, merge_blocks

# python3.9 -m pytest


def test_extract_number():
    assert extract_number('A1') == 1
    assert extract_number('B100') == 100


def test_extract_column():
    assert extract_column('A1') == 'A'
    assert extract_column('AA23') == 'AA'


def test_generate_solid_blocks():
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
        blocks['DATA']) == 1, f"Failed to generate solid blocks, expected 1 DATA block, got {len(blocks['DATA'])}"
    assert len(
        blocks['LABEL']) == 1, f"Failed to generate solid blocks, expected 1 LABEL block, got {len(blocks['LABEL'])}"

# Test the case of non-sequential cell names


@pytest.mark.dependency()
def test_non_sequential_cells():
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
        merged_blocks['DATA']) == 3, f"Failed to handle non-sequential cells, expected 3 cells, got {len(merged_blocks['DATA'])}"

# Test the case of varied block lengths


@pytest.mark.dependency()
def test_varied_block_lengths():
    # Prepare a mock sheet with blocks of different lengths
    sheet = {
        "Sheet number": 1,
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "A2": {"annotation": "DATA"},
            "B1": {"annotation": "DATA"},
            "C1": {"annotation": "DATA"},
            "C2": {"annotation": "DATA"},
            "C3": {"annotation": "DATA"},
        }
    }

    # Generate and merge blocks
    blocks = generate_solid_blocks(sheet)
    merged_blocks = merge_blocks(blocks)

    # Verify the result
    assert len(
        merged_blocks['DATA']) == 3, f"Failed to handle blocks of varied lengths, expected 3 blocks, got {len(merged_blocks['DATA'])}"

# Test the case of special characters in cell names


@pytest.mark.dependency(depends=["test_non_sequential_cells",
                        "test_varied_block_lengths"])
def test_special_characters():
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
        merged_blocks['DATA']) == 2, f"Failed to handle special characters in cell names, expected 3 cells, got {len(merged_blocks['DATA'])}"

# Test the case of empty sheets


def test_empty_sheet():
    # Prepare a mock empty sheet
    sheet = {
        "Sheet number": 1,
        "Annotations": {}
    }

    # Generate and merge blocks
    blocks = generate_solid_blocks(sheet)
    merged_blocks = merge_blocks(blocks)

    # Verify the result
    assert len(merged_blocks) == 0, "Failed to handle empty sheets"


def test_merge_blocks():
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
        merged_blocks['DATA']) == expected_data_length, f"Expected {expected_data_length} merged DATA block(s), but got {len(merged_blocks['DATA'])}"

    # Assert the length of merged_blocks['LABEL']
    expected_LABEL_length = 1
    assert len(
        merged_blocks['LABEL']) == expected_LABEL_length, f"Expected {expected_LABEL_length} merged LABEL block(s), but got {len(merged_blocks['LABEL'])}"


def test_empty_input():
    blocks = generate_solid_blocks({"Annotations": {}})
    assert blocks == defaultdict(list)


def test_output(tmp_path):
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
