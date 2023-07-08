import pytest
import src.python.Identification.LB_ID as lb
# python3.9 -m pytest -v tests/TEST_LB_ID.py

# Test data
valid_input_data = {
    "assembly": {
        "row": 5,
        "column": 5
    },
    "solid_tables_output": {
        "assembly": {
            "sheet": {
                "name": "sheet1",
                "properties": {
                    "sheet_number": 1,
                    "solid_tables": {
                        "properties": {
                            "data": {
                                "start": {"row": 1, "column": 1},
                                "end": {"row": 3, "column": 3}
                            }
                        },
                        "labels": {
                            "assembly": {
                                "positioned_label": {
                                    "name": "label1"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

invalid_input_data = {
    "assembly": {
        "row": -5,
        "column": -5
    }
}


@pytest.mark.dependency()
@pytest.mark.dependency()
def test_check_for_potential_light_blocks():
    # Example for positive scenario
    data_block = {
        "x_size": 2,
        "y_size": 2,
        "start_pos": {
            'l0': [0, 2],
            'l1': [0, 3],
            'r0': [2, 2],
            'r1': [3, 2],
            't0': [1, 1],
            't1': [1, 0],
            'b0': [1, 3],
            'b1': [1, 4],
        }
    }
    free_labels = [
        {
            'x_size': 1,
            'y_size': 1,
            'pos': {
                'start': [0, 2]
            }
        }
    ]
    expected_output = [{
        'x_size': 1,
        'y_size': 1,
        'pos': {
            'start': [0, 2],
            'end': [0, 2]
        },
        'poisition': 'l0'
    }]
    assert lb.check_for_potential_light_blocks(data_block, free_labels) == expected_output, "Failed to identify potential light block locations correctly"

@pytest.mark.dependency(depends=["test_check_for_potential_light_blocks"])
def test_label_light_block_search():
    # Mock data setup
    table = {
        'data': {
            'start_pos': {
                'l0': [0, 2],
                'l1': [0, 3],
                'r0': [2, 2],
                'r1': [3, 2],
                't0': [1, 1],
                't1': [1, 0],
                'b0': [1, 3],
                'b1': [1, 4],
            }
        },
    }
    free_labels = [
        {
            'x_size': 1,
            'y_size': 1,
            'pos': {
                'start': [0, 2]
            }
        }
    ]

    # Positive scenario: Light Block label is smaller than table data block
    expected_result = [{
        'pos': {
            'start': [0, 2],
            'end': [0, 2]
        },
        'x_size': 1,
        'y_size': 1,
        'position': 'l0'
    }]
    assert lb.label_light_block_search(table, free_labels) == expected_result, "Failed to identify light block label when it's smaller than the table's data block"
    
    # Negative scenario: Light Block label is larger than table data block
    free_labels[0]['x_size'] = 3
    expected_result = []
    assert lb.label_light_block_search(table, free_labels) == expected_result, "Failed to handle light block label larger than the table's data block"

    # Edge case: Light Block label size is the same as table data block
    free_labels[0]['x_size'] = 2
    expected_result = []
    assert lb.label_light_block_search(table, free_labels) == expected_result, "Failed to handle light block label of same size as the table's data block"

    # Negative scenario: No free blocks available
    free_labels = []
    expected_result = []
    assert lb.label_light_block_search(table, free_labels) == expected_result, "Failed to handle no free blocks scenario"


@pytest.mark.dependency(depends=["test_label_light_block_search"])
def test_pattern_ab_search():
    # Positive Scenario
    data_blocks = [{'start_row': 1, 'end_row': 2, 'start_column': 'A', 'end_column': 'A'},
                   {'start_row': 3, 'end_row': 4, 'start_column': 'A', 'end_column': 'A'}]
    labels = [{'start_row': 1, 'end_row': 4, 'start_column': 'B', 'end_column': 'B'}]
    assert lb.pattern_ab_search(data_blocks, labels) == [{'start_row': 1, 'end_row': 4, 'start_column': 'A', 'end_column': 'B'}], "Failed to identify pattern AB correctly"

    # Edge Case - Blocks do not form pattern AB
    data_blocks = [{'start_row': 1, 'end_row': 2, 'start_column': 'A', 'end_column': 'A'},
                   {'start_row': 4, 'end_row': 5, 'start_column': 'A', 'end_column': 'A'}]
    labels = [{'start_row': 1, 'end_row': 3, 'start_column': 'B', 'end_column': 'B'}]
    assert lb.pattern_ab_search(data_blocks, labels) == [], "Failed to handle edge case where blocks do not form pattern AB"

    # Negative Scenario - No Data Blocks
    assert lb.pattern_ab_search([], labels) == [], "Failed to handle scenario with no data blocks"


@pytest.mark.dependency(depends=["test_label_light_block_search"])
def test_pattern_bb_search():
    # Positive Scenario
    data_blocks = [{'start_row': 1, 'end_row': 2, 'start_column': 'A', 'end_column': 'A'},
                   {'start_row': 4, 'end_row': 5, 'start_column': 'A', 'end_column': 'A'}]
    labels = [{'start_row': 1, 'end_row': 2, 'start_column': 'B', 'end_column': 'B'},
              {'start_row': 4, 'end_row': 5, 'start_column': 'B', 'end_column': 'B'}]
    assert lb.pattern_bb_search(data_blocks, labels) == [{'start_row': 1, 'end_row': 2, 'start_column': 'A', 'end_column': 'B'},
                                                      {'start_row': 4, 'end_row': 5, 'start_column': 'A', 'end_column': 'B'}], "Failed to identify pattern BB correctly"

    # Edge Case - Blocks do not form pattern BB
    data_blocks = [{'start_row': 1, 'end_row': 2, 'start_column': 'A', 'end_column': 'A'},
                   {'start_row': 4, 'end_row': 5, 'start_column': 'A', 'end_column': 'A'}]
    labels = [{'start_row': 1, 'end_row': 3, 'start_column': 'B', 'end_column': 'B'}]
    assert lb.pattern_bb_search(data_blocks, labels) == [], "Failed to handle edge case where blocks do not form pattern BB"

    # Negative Scenario - No Label Blocks
    assert lb.pattern_bb_search(data_blocks, []) == [], "Failed to handle scenario with no label blocks"


@pytest.mark.dependency(depends=["test_label_light_block_search"])
def test_pattern_cb_search():
    # Positive Scenario
    data_blocks = [{'start_row': 1, 'end_row': 2, 'start_column': 'A', 'end_column': 'A'},
                   {'start_row': 4, 'end_row': 5, 'start_column': 'A', 'end_column': 'A'}]
    labels = [{'start_row': 1, 'end_row': 5, 'start_column': 'B', 'end_column': 'B'}]
    assert lb.pattern_cb_search(data_blocks, labels) == [{'start_row': 1, 'end_row': 5, 'start_column': 'A', 'end_column': 'B'}], "Failed to identify pattern CB correctly"

    # Edge Case - Blocks do not form pattern CB
    data_blocks = [{'start_row': 1, 'end_row': 2, 'start_column': 'A', 'end_column': 'A'},
                   {'start_row': 4, 'end_row': 5, 'start_column': 'A', 'end_column': 'A'}]
    labels = [{'start_row': 1, 'end_row': 3, 'start_column': 'B', 'end_column': 'B'}]
    assert lb.pattern_cb_search(data_blocks, labels) == [], "Failed to handle edge case where blocks do not form pattern CB"

    # Negative Scenario - No Data Blocks
    assert lb.pattern_cb_search([], labels) == [], "Failed to handle scenario with no data blocks"


@pytest.mark.dependency(depends=["test_pattern_cb_search", "test_pattern_bb_search", "test_pattern_ab_search"])
def test_identify_light_blocks():
    # Example for positive scenario
    input_data = {"sheet1": { "solid_tables": [ { "data": { "start_row": 1, "end_row": 5, "start_column": "A", "end_column": "E" }, "labels": { "b1": { "start_row": 6, "end_row": 6, "start_column": "A", "end_column": "E" } } } ], "free_solid_blocks": { "LABEL": [], "DATA": [] } } }
    expected_output = {"sheet1": { "solid_tables": [ { "data": { "start_row": 1, "end_row": 5, "start_column": "A", "end_column": "E" }, "labels": { "b1": { "start_row": 6, "end_row": 6, "start_column": "A", "end_column": "E" } }, "light_blocks": [ { "start_row": 1, "end_row": 5, "start_column": "F", "end_column": "F" } ] } ], "free_solid_blocks": { "LABEL": [], "DATA": [] } } }
    assert lb.identify_light_blocks(input_data) == expected_output, "Failed to identify light blocks correctly"

    # Edge case
    empty_data = {}
    assert lb.identify_light_blocks(empty_data) == {}, "Failed to handle empty data"

    edge_case_data = valid_input_data.copy()
    edge_case_data['assembly']['row'] = 0
    assert lb.identify_light_blocks(
        edge_case_data) is not None, "Failed to handle edge case input data"


    #Negative case
    with pytest.raises(ValueError) as error:
        lb.identify_light_blocks(
            invalid_input_data)
    assert str(error.value) == "Failed to raise error for invalid input data"

    #Special large data case
    large_scale_data = valid_input_data.copy()
    large_scale_data['assembly']['row'] = 10000
    large_scale_data['assembly']['column'] = 10000
    assert lb.identify_light_blocks(
        large_scale_data) is not None, "Failed to handle large scale input data"
    
    #null values
    null_values_data = valid_input_data.copy()
    null_values_data['assembly']['row'] = None
    with pytest.raises(ValueError) as error:
        lb.identify_light_blocks(
            null_values_data)
    assert str(error.value) == "Failed to handle null values in input data"

    #multiple assemblies
    multiple_assemblies_data = valid_input_data.copy()
    multiple_assemblies_data['assembly'] = [
        {'row': 5, 'column': 5}, {'row': 6, 'column': 6}]
    assert lb.identify_light_blocks(
        multiple_assemblies_data) is not None, "Failed to handle multiple assemblies"
