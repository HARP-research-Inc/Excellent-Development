import pytest
#import openai
import os
from src.python.chunker import join_or_concat_with_proper_alignment, cut_csv_into_chunks, chunk_sheet, print_output_json
from src.python.annotator import get_annotated_chunk, annotate_cells_ai

def test_join_or_concat_with_proper_alignment_positive():
    assert join_or_concat_with_proper_alignment(
        [['A1', 'B1'], ['A2', 'B2']],
        [['C1', 'D1'], ['C2', 'D2']],
        'join'
    ) == [['C1', 'D1', 'A1', 'B1'], ['C2', 'D2', 'A2', 'B2']], "Failed to handle valid lists with action 'join'"
    
    assert join_or_concat_with_proper_alignment(
        [['A1', 'B1'], ['A2', 'B2']],
        [['C1', 'D1'], ['C2', 'D2']],
        'concat'
    ) == [['A1', 'B1'], ['A2', 'B2'], ['C1', 'D1'], ['C2', 'D2']], "Failed to handle valid lists with action 'concat'"

def test_join_or_concat_with_proper_alignment_edge_cases():
    assert join_or_concat_with_proper_alignment([], [['C1', 'D1'], ['C2', 'D2']], 'join') == [['C1', 'D1'], ['C2', 'D2']], "Failed to handle empty list1"
    assert join_or_concat_with_proper_alignment([['A1', 'B1'], ['A2', 'B2']], [], 'join') == [['A1', 'B1'], ['A2', 'B2']], "Failed to handle empty list2"

def test_cut_csv_into_chunks():
    csv_data = 'A,B,C\n1,2,3\n4,5,6\n7,8,9'
    chunk_size = 2
    context_size = 1
    result = cut_csv_into_chunks(csv_data, chunk_size, context_size)
    assert len(result) == 2, "Failed to divide the csv data into correct number of chunks"

def test_chunk_sheet():
    csv_data = 'A,B,C\n1,2,3\n4,5,6\n7,8,9'
    chunk_size = 2
    context_size = 1
    result = chunk_sheet(csv_data, chunk_size, context_size, "Test Sheet")
    assert '"Sheet Test Sheet"' in result, "Failed to include the sheet name in the output json"

@pytest.mark.parametrize("csv_data, chunk_size, context_size, name", [
    ('A,B,C\n1,2,3\n4,5,6\n7,8,9', 2, 1, "Test Sheet"),
])
def test_print_output_json(capsys, csv_data, chunk_size, context_size, name):
    output_json = chunk_sheet(csv_data, chunk_size, context_size, name)
    print_output_json(output_json, [csv_data])
    captured = capsys.readouterr()
    assert "Sheet Test Sheet" in captured.out, "Failed to print the sheet name"


def test_get_annotated_chunk():
    chunk = [[('A1', 'column1'), ('A2', 'data1')], [('B1', 'column2'), ('B2', 'data2')]]
    current_cell_id = 'A1'
    annotated_output = {'A1': {'value': 'column1', 'annotation': 'LABEL'}}
    result = get_annotated_chunk(chunk, current_cell_id, annotated_output)
    assert '[LABEL] column1' in result, "Failed to annotate a label cell"

def test_annotate_cells_ai(mocker):
    mocker.patch.object(openai, 'Completion')
    output_dict = {'Sheet 1': {'Row 1': {'Chunk 1': {'base_chunk': [[('A1', 'column1')]], 'contextualized_chunk': [[('A1', 'column1')]]}}}}
    openai_api_key = os.getenv('openai_api_key')
    openai.Completion.create.return_value = mocker.MagicMock(choices=[mocker.MagicMock(text='Y')])
    result = annotate_cells_ai(output_dict, openai_api_key)
    assert result[0]['Sheet 1']['A1']['annotation'] == 'LABEL', "Failed to annotate a label cell"

import pytest
from sheet import Sheet, cel

def test_sb_id_valid_cells():
    cells = [cel(coord=(0, 0), block_type="DATA"), cel(coord=(1, 0), block_type="LABEL")]
    sheet = Sheet(name='Test Sheet', cells=cells)
    sheet.sb_id()
    
    assert len(sheet.blocks) > 0, "Failed to create blocks from valid cells"
    assert all(isinstance(block, blk) for block in sheet.blocks), "Failed to create valid blocks from cells"

# Additional test cases can be added to test different types of cells and block types
