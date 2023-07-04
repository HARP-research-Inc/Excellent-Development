import json
from collections import defaultdict
import pytest
import src.python.Identification.ST_ID as st
import os, sys


# 2. Negative test case for the function initialize_sheets
def  test_initialize_sheets_fail():
    with pytest.raises(ValueError, match="Unexpected Block Type"):
        st.initialize_sheets({})

# 3. Positive test case for the function excel_column_number
def  test_excel_column_number():
    assert st.excel_column_number("A") == 1, "Failed to convert A to 1"
    assert st.excel_column_number("Z") == 26, "Failed to convert Z to 26"
    assert st.excel_column_number("AA") == 27, "Failed to convert AA to 27"

# 4. Negative test case for the function excel_column_number
def  test_excel_column_number_fail():
    assert st.excel_column_number("1") == 0, "Failed to handle numeric input"

# 5. Edge case for the function excel_column_number
def  test_excel_column_number_edge():
    assert st.excel_column_number("AAA") == 703, "Failed to handle large input"

# 6. Positive test case for the function excel_column_letter
def  test_excel_column_letter():
    assert st.excel_column_letter(1) == "A", "Failed to convert 1 to A"
    assert st.excel_column_letter(26) == "Z", "Failed to convert 26 to Z"
    assert st.excel_column_letter(27) == "AA", "Failed to convert 27 to AA"

# 7. Negative test case for the function excel_column_letter
def  test_excel_column_letter_fail():
    assert st.excel_column_letter(0) == "", "Failed to handle zero input"

# 8. Edge case for the function excel_column_letter
def  test_excel_column_letter_edge():
    assert st.excel_column_letter(703) == "AAA", "Failed to handle large input"

# 9. Test for initialize_tabulate_and_export function with valid input file
def  test_initialize_tabulate_and_export():
    input_file = "src/python/JSONs/blocks_output.json"
    output_file = "src/python/JSONs/solid_table_output.json"
    st.initialize_tabulate_and_export(input_file, output_file, debug=False)
    # Check if output file is created and is not empty
    assert os.path.exists(output_file), "Output file does not exist"
    with open(output_file, "r") as f:
        data = json.load(f)
    assert data is not None, "Output file is empty"

# 10. Test for initialize_tabulate_and_export function with invalid input file
def  test_initialize_tabulate_and_export_fail():
    input_file = "invalid_file.json"
    output_file = "output.json"
    with pytest.raises(FileNotFoundError):
        st.initialize_tabulate_and_export(input_file, output_file)
