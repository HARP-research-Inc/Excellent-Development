import pytest
from src.python.SB_ID.rectangle_algorithm import Rec_Algo
from src.python.structures.cell import Cell as cel
from src.python.structures.block import Block as blk
from src.python.structures.sheet import Sheet as sht

def test_sb_id_empty_cells():
    sheetq = sht(name='Tet Sheet')
    print(sheetq)
    sheetq.sb_id()
    
    assert len(sheetq.blocks) == 0, "Failed to handle empty cells"

def test_sb_id_mixed_block_types():
    cells = [cel(location=(1, 1), value="testd", annotation="DATA"), cel(location=(2, 1), value="testl", annotation="EMPTY")]
    sheet = sht(name='Test Sheet', cells=cells)
    sheet.sb_id()
    
    assert len(sheet.blocks) == 1, "Failed to handle empty block type"

def test_sb_id_valid_cells():
    cells = [cel(location=(1, 1), value="testd", annotation="DATA"), cel(location=(2, 1), value="testl", annotation="LABEL")]
    sheet = sht(name='Test Sheet', cells=cells)
    sheet.sb_id()
    
    assert len(sheet.blocks) == 2, "Failed to create blocks from valid cells"
    assert all(isinstance(block, blk) for block in sheet.blocks), "Failed to create valid blocks from cells"
