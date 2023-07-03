import json
from collections import defaultdict
import pytest
from Identification.SB_ID import extract_number, extract_column, generate_solid_blocks, merge_blocks

#python3.9 -m pytest

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
            "A2": {"annotation": "FORMULA"},
            "B2": {"annotation": "FORMULA"},
        }
    }
    blocks = generate_solid_blocks(sheet1)
    assert len(blocks['DATA']) == 1
    assert len(blocks['FORMULA']) == 1


def test_merge_blocks():
    sheet1 = {
        "Annotations": {
            "A1": {"annotation": "DATA"},
            "B1": {"annotation": "DATA"},
            "A2": {"annotation": "FORMULA"},
            "B2": {"annotation": "FORMULA"},
        }
    }
    blocks = generate_solid_blocks(sheet1)
    merged_blocks = merge_blocks(blocks)
    assert len(merged_blocks['DATA']) == 1
    assert len(merged_blocks['FORMULA']) == 1


def test_empty_input():
    blocks = generate_solid_blocks({"Annotations": {}})
    assert blocks == defaultdict(list)


def test_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        with open("JSONs/invalid_file.json", "r") as file:
            data = json.load(file)


def test_non_existent_file():
    with pytest.raises(FileNotFoundError):
        with open("non_existent_file.json", "r") as file:
            data = json.load(file)


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


