from src.open_ai_demo_python.gen_tree import cell, block, sheet, table, gen_tree
from src.open_ai_demo_python.ST_ID import st_id  # replace 'your_module' with the actual module name where st_id is defined
import json
def test_st_id():
    # Prepare input data
    cells = [
        cell((1, 1), "Date", "LABEL"),
        cell((1, 2), "Time", "LABEL"),
        cell((1, 3), "Country", "LABEL"),
        cell((2, 1), "George Costanza", "LABEL"),
        cell((2, 2), "10/12/2023", "DATA"),
        cell((2, 3), "10:15", "DATA"),
        cell((2, 4), "USA", "DATA"),
        cell((3, 1), "Bill Jeofry", "LABEL"),
        cell((3, 2), "09/01/2002", "DATA"),
        cell((3, 3), "14:30", "DATA"),
        cell((3, 4), "UK", "DATA"),
        cell((4, 1), "Harper Giorgo", "LABEL"),
        cell((4, 2), "11/22/1963", "DATA"),
        cell((4, 3), "13:45", "DATA"),
        cell((4, 4), "Canada", "DATA"),
    ]
    input_tree = gen_tree(sheets=[sheet(name="Sheet1", cells=cells)])

    # Call the function with the prepared input
    output_tree = st_id(input_tree)

    # Prepare expected output
    label_blocks = [
        block(annotation_type="LABEL", cells=[cell((1, 1), "Date", "LABEL"),
                                              cell((1, 2), "Time", "LABEL"),
                                              cell((1, 3), "Country", "LABEL")]),
        block(annotation_type="LABEL", cells=[cell((2, 1), "George Costanza", "LABEL"),
                                              cell((3, 1), "Bill Jeofry", "LABEL"),
                                              cell((4, 1), "Harper Giorgo", "LABEL")])
    ]
    data_blocks = [
        block(annotation_type = "DATA", cells=[
            cell((2, 2), "10/12/2023", "DATA"), cell((2, 3), "10:15", "DATA"), cell((2, 4), "USA", "DATA"), 
            cell((3, 2), "09/01/2002", "DATA"), cell((3, 3), "14:30", "DATA"), cell((3, 4), "UK", "DATA"), 
            cell((4, 2), "11/22/1963", "DATA"), cell((4, 3), "13:45", "DATA"), cell((4, 4), "Canada", "DATA")
        ])
    ]
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
    expected_output_tree = gen_tree(sheets=[sheet(name="Sheet1", tables=tables)])

    # Assert that the function output is as expected
    assert output_tree.to_json() == expected_output_tree.to_json(), f"expected {json.dump(expected_output_tree.to_clean_json())}, got {json.dump(output_tree.to_clean_json())}"
