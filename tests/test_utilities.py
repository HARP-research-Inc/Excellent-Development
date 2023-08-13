import pandas as pd
import pytest
from src.python.structures.utilities import Gen_Tree_Helper as gth
#Title: TESTS Utilities
#Author: Harper Chisari

#Version History:
#Harper: 8/12/23 - initial commit


# Step 1: Specify Fixtures
@pytest.fixture(scope='session')
def base_df():
    return pd.DataFrame([[" "] * 5] * 5)

@pytest.fixture(scope='session')
def source_df():
    return pd.DataFrame({'A': [1, 2], 'B': [3, 4]})

# Step 2a: Positive test cases
@pytest.mark.dependency()
def test_insert_dataframe_valid(base_df, source_df):
    relative_origin = (2, 2)
    result_df = gth.insert_dataframe(base_df.copy(), source_df, relative_origin)
    expected_output = pd.DataFrame([
        [" ", " ", " ", " ", " "],
        [" ", 1, 3, " ", " "],
        [" ", 2, 4, " ", " "],
        [" ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " "]
    ])
    print("Result DataFrame:")
    print(result_df)
    print("Expected DataFrame:")
    print(expected_output)
    assert result_df.equals(expected_output), "Failed to correctly insert the source dataframe at the given relative origin"


# Step 2b: Negative test cases
@pytest.mark.dependency()
def test_insert_dataframe_invalid_origin(base_df, source_df):
    relative_origin = (0, 0) # Invalid origin
    with pytest.raises(ValueError):
        gth.insert_dataframe(base_df, source_df, relative_origin)
    # Expecting an error due to invalid origin

# Step 2c: Edge cases
@pytest.mark.dependency(depends=['test_insert_dataframe_valid'])
def test_insert_dataframe_edge_case(base_df, source_df):
    relative_origin = (5, 5) # Edge case where source_df will extend beyond base_df
    result_df = gth.insert_dataframe(base_df.copy(), source_df, relative_origin)
    expected_output = pd.DataFrame([
        [" ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", 1, 3],
        [" ", " ", " ", " ", 2, 4],
    ])
    print("Result DataFrame:")
    print(result_df)
    print("Expected DataFrame:")
    print(expected_output)
    assert result_df.equals(expected_output), "Failed to handle the insertion at the edge of the base dataframe"

# Step 3: Include negative scenarios
@pytest.mark.dependency()
def test_insert_dataframe_empty_sheets(base_df):
    source_df = pd.DataFrame() # Empty source DataFrame
    relative_origin = (2, 2)
    result_df = gth.insert_dataframe(base_df.copy(), source_df, relative_origin)
    assert result_df.equals(base_df), "Failed to handle empty sheets"

# Additional test cases can be created to explore boundary conditions (Step 6),
# consider equivalence classes (Step 5), and consider special scenarios (Step 8).
