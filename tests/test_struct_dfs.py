import pytest
import pandas as pd
from src.python.structures.cell import Cell as cell
from src.python.structures.block import Block as block
from src.python.structures.table import Table as table
from src.python.structures.sheet import Sheet as sheet

# Title: test_structures.py
# Author: Harper Chisari
# Description: Test suite for testing structures including cells, blocks, tables, and sheets. Includes various cases for testing the conversion to dataframes.
# Contents:
#   - Test Objects: Defines various objects to be used in the tests
#   - test_single_to_dataframe: Tests the conversion of a single cell to a DataFrame
#   - test_multiple_label_to_dataframe: Tests the conversion of a single row label block to a DataFrame
#   - test_multiple_vertical_label_to_dataframe: Tests the conversion of a single column label block to a DataFrame
#   - test_data_block_to_dataframe: Tests the conversion of a data block to a DataFrame
#   - test_table_to_dataframe: Tests the conversion of a table to a DataFrame
#   - test_sheet_to_dataframe: Tests the conversion of a sheet to a DataFrame
# Version History:
#   Harper: 8/12/23 - v1.2: added titleblock, totally revamped tests

#@pytest.fixture(scope = 'session')
# Sheet Label
cell_01 = cell(location=(1,1), value='Business Performance', annotation="LABEL")
label_block_01 = block(cells=[cell_01])
label_1_df = pd.DataFrame([["Business Performance"]])

@pytest.mark.dependency()
def test_single_to_dataframe():
    df_b_01 = label_block_01.to_dataframe()
    print("Result DataFrame:")
    print(df_b_01)
    print("Expected DataFrame:")
    print(label_1_df)
    assert df_b_01.equals(label_1_df), "Failed to correctly populate dataframe from a block of a single cell"

#Table 1
cell_02 = cell(location=(2,3), value='Sales', annotation="LABEL")
cell_03 = cell(location=(3,3), value='Services', annotation="LABEL")
label_block_02 = block(cells=[cell_02, cell_03])
label_2_df = pd.DataFrame([["Sales","Services"]])

@pytest.mark.dependency(depends=['test_single_to_dataframe'])
def test_multiple_label_to_dataframe():
    lb_2_df = label_block_02.to_dataframe()
    print("Result DataFrame:")
    print(lb_2_df)
    print("Expected DataFrame:")
    print(label_2_df)
    assert lb_2_df.equals(label_2_df), "Failed to correctly populate dataframe from a single row label block"

cell_010 = cell(location=(1,4), value='Q1', annotation="LABEL")
cell_011 = cell(location=(1,5), value='Q2', annotation="LABEL")
cell_012 = cell(location=(1,6), value='Q3', annotation="LABEL")
cell_013 = cell(location=(1,7), value='Q4', annotation="LABEL")
cell_019 = cell(location=(1,8), value='Total', annotation="LABEL")
label_block_05 = block(cells=[cell_010, cell_011, cell_012, cell_013, cell_019])
label_5_df = pd.DataFrame([
    ["Q1"],
    ["Q2"],
    ["Q3"],
    ["Q4"],
    ["Total"]])

@pytest.mark.dependency(depends=['test_single_to_dataframe'])
def test_multiple_vertical_label_to_dataframe():
    lb_5_df = label_block_05.to_dataframe()
    print("Result DataFrame:")
    print(lb_5_df)
    print("Expected DataFrame:")
    print(label_5_df)
    assert lb_5_df.equals(label_5_df), "Failed to correctly populate dataframe from a single column label block"

cell_1 = cell(location=(2,4), value='100000', annotation="DATA")
cell_2 = cell(location=(3,4), value='50000', annotation="DATA")
cell_3 = cell(location=(2,5), value='120000', annotation="DATA")
cell_4 = cell(location=(3,5), value='60000', annotation="DATA")
cell_5 = cell(location=(2,6), value='110000', annotation="DATA")
cell_6 = cell(location=(3,6), value='55000', annotation="DATA")
cell_7 = cell(location=(2,7), value='130000', annotation="DATA")
cell_8 = cell(location=(3,7), value='65000', annotation="DATA")
cell_21 = cell(location=(2,8), value='=SUM(B4:B7)', annotation="FORMULA")
cell_22 = cell(location=(3,8), value='=SUM(C4:C7)', annotation="FORMULA")
data_block_01 = block(cells=[cell_1, cell_2, cell_3, cell_4, cell_5, cell_6, cell_7, cell_8, cell_21, cell_22])
data_1_df = pd.DataFrame([["100000","50000"],
    ["120000","60000"],
    ["110000","55000"],
    ["130000","65000"],
    ["=SUM(B4:B7)","=SUM(C4:C7)"]])

@pytest.mark.dependency(depends=['test_multiple_vertical_label_to_dataframe'])
def test_data_block_to_dataframe():
    db_1_df = data_block_01.to_dataframe()
    print("Result DataFrame:")
    print(db_1_df)
    print("Expected DataFrame:")
    print(data_1_df)
    assert db_1_df.equals(data_1_df), "Failed to correctly populate dataframe from a data block"

table_1 = table(t0=label_block_02, l0=label_block_05, data_block=data_block_01)

table_1_df = pd.DataFrame([[" ","Sales","Services"],
    ["Q1","100000","50000"],
    ["Q2","120000","60000"],
    ["Q3","110000","55000"],
    ["Q4","130000","65000"],
    ["Total","=SUM(B4:B7)","=SUM(C4:C7)"]])

table_11 = table(t0=label_block_02, l0=label_block_05, data_block=data_block_01, free_labels=[label_block_01])

table_11_df = 0
table_11_df = pd.DataFrame([["Business Performance"," "," "],
    [" "," "," "],
    [" ","Sales","Services"],
    ["Q1","100000","50000"],
    ["Q2","120000","60000"],
    ["Q3","110000","55000"],
    ["Q4","130000","65000"],
    ["Total","=SUM(B4:B7)","=SUM(C4:C7)"],])

label_block_101 = block(cells=[cell(location=(1,1), value='Business Performance', annotation="DATA")])
table_21 = table(t0=label_block_02, l0=label_block_05, data_block=data_block_01, free_labels=[label_block_101])

table_21_df = pd.DataFrame([["Business Performance"," "," "],
    [" "," "," "],
    [" ","Sales","Services"],
    ["Q1","100000","50000"],
    ["Q2","120000","60000"],
    ["Q3","110000","55000"],
    ["Q4","130000","65000"],
    ["Total","=SUM(B4:B7)","=SUM(C4:C7)"]])

@pytest.mark.dependency(depends=['test_data_block_to_dataframe'])
def test_table_to_dataframe():
    tb_1_df = table_1.to_dataframe()
    tb_11_df = table_11.to_dataframe()
    tb_21_df = table_21.to_dataframe()
    print("Result DataFrame:")
    print(tb_1_df)
    print("Expected DataFrame:")
    print(table_1_df)
    assert tb_1_df.equals(table_1_df), "Failed to correctly populate dataframe from a table"
    print("Original DataFrame:")
    print(tb_1_df)
    print("Result DataFrame:")
    print(tb_11_df)
    print("Expected DataFrame:")
    print(table_11_df)
    assert tb_11_df.equals(table_11_df), "Failed to correctly populate dataframe with free label from a table"
    print("Result DataFrame:")
    print(tb_21_df)
    print("Expected DataFrame:")
    print(table_21_df)
    assert tb_21_df.equals(table_21_df), "Failed to correctly populate dataframe with free data from a table"

#Table 2
cell_04 = cell(location=(6,6), value='Value', annotation="LABEL")
label_block_03 = block(cells=[cell_04])
label_3_df = pd.DataFrame([["Value"]])

cell_05 = cell(location=(5,7), value='Net Profit', annotation="LABEL")
cell_06 = cell(location=(5,8), value='Profit Margin', annotation="LABEL")
label_block_04 = block(cells=[cell_06, cell_05])
label_4_df = pd.DataFrame([["Net Profit"],["Profit Margin"]])

cell_27 = cell(location=(6,7), value='822000', annotation="DATA")
cell_23 = cell(location=(6,8), value='=(B8/(B8+C8))*100', annotation="FORMULA")
data_block_02 = block(cells=[cell_27, cell_23])
data_2_df = pd.DataFrame([["822000"],["=(B8/(B8+C8))*100"]])

table_2 = table(t0=label_block_03, l0=label_block_04, data_block=data_block_02)
tabel_2_df = pd.DataFrame([[" ","Value"],
    ["Net Profit","822000"],
    ["Profit Margin","=(B8/(B8+C8))*100"]])

#Table 3
cell_07 = cell(location=(2,10), value='Salary', annotation="LABEL")
cell_08 = cell(location=(3,10), value='Rent', annotation="LABEL")
cell_09 = cell(location=(4,10), value='Marketing', annotation="LABEL")
label_block_06 = block(cells=[cell_07, cell_08, cell_09])
label_6_df = pd.DataFrame([["Salary", "Rent", "Marketing"]])

cell_014 = cell(location=(1,11), value='Q1', annotation="LABEL")
cell_015 = cell(location=(1,12), value='Q2', annotation="LABEL")
cell_016 = cell(location=(1,13), value='Q3', annotation="LABEL")
cell_017 = cell(location=(1,14), value='Q4', annotation="LABEL")
cell_018 = cell(location=(1,15), value='Total', annotation="LABEL")
label_block_07 = block(cells=[cell_014, cell_015, cell_016, cell_017, cell_018])
label_7_df = pd.DataFrame([
    ["Q1"],
    ["Q2"],
    ["Q3"],
    ["Q4"],
    ["Total"]])

cell_9 = cell(location=(2,11), value='40000', annotation="DATA")
cell_10 = cell(location=(3,11), value='10000', annotation="DATA")
cell_11 = cell(location=(4,11), value='15000', annotation="DATA")
cell_12 = cell(location=(2,12), value='42000', annotation="DATA")
cell_13 = cell(location=(3,12), value='10000', annotation="DATA")
cell_14 = cell(location=(4,12), value='18000', annotation="DATA")
cell_15 = cell(location=(2,13), value='43000', annotation="DATA")
cell_16 = cell(location=(3,13), value='10000', annotation="DATA")
cell_17 = cell(location=(4,13), value='17000', annotation="DATA")
cell_18 = cell(location=(2,14), value='45000', annotation="DATA")
cell_19 = cell(location=(3,14), value='10000', annotation="DATA")
cell_20 = cell(location=(4,14), value='19000', annotation="DATA")
cell_24 = cell(location=(2,15), value='=SUM(B11:B14)', annotation="FORMULA")
cell_25 = cell(location=(3,15), value='=SUM(C11:C14)', annotation="FORMULA")
cell_26 = cell(location=(4,15), value='=SUM(D11:D14)', annotation="FORMULA")
data_block_03 = block(cells=[cell_9, cell_10, cell_11, cell_12, cell_13, cell_14, cell_15, cell_16, cell_17, cell_18, cell_19, cell_20, cell_24, cell_25, cell_26])

data_3_df = pd.DataFrame([
    ["40000","10000","15000"],
    ["42000","10000","18000"],
    ["43000","10000","17000"],
    ["45000","10000","19000"],
    ["=SUM(B11:B14)","=SUM(C11:C14)","=SUM(D11:D14)"]])

table_3 = table(t0=label_block_06, l0=label_block_07, data_block=data_block_03)

table_3_df = pd.DataFrame([[" ","Salary","Rent","Marketing"," "," "],
    ["Q1","40000","10000","15000"," "," "],
    ["Q2","42000","10000","18000"," "," "],
    ["Q3","43000","10000","17000"," "," "],
    ["Q4","45000","10000","19000"," "," "],
    ["Total","=SUM(B11:B14)","=SUM(C11:C14)","=SUM(D11:D14)"," "," "]])

sheet_1 = sheet(name="Business Performance", tables=[table_1, table_2, table_3], free_labels=[label_block_01])

sheet_1_df = pd.DataFrame([["Business Performance"," "," "," "," "," "],
    [" "," "," "," "," "," "],
    [" ","Sales","Services"," "," "," "],
    ["Q1","100000","50000"," "," "," "],
    ["Q2","120000","60000"," "," "," "],
    ["Q3","110000","55000"," "," ","Value"],
    ["Q4","130000","65000"," ","Net Profit","822000"],
    ["Total","=SUM(B4:B7)","=SUM(C4:C7)"," ","Profit Margin","=(B8/(B8+C8))*100"],
    [" "," "," "," "," "," "],
    [" ","Salary","Rent","Marketing"," "," "],
    ["Q1","40000","10000","15000"," "," "],
    ["Q2","42000","10000","18000"," "," "],
    ["Q3","43000","10000","17000"," "," "],
    ["Q4","45000","10000","19000"," "," "],
    ["Total","=SUM(B11:B14)","=SUM(C11:C14)","=SUM(D11:D14)"," "," "]])


@pytest.mark.dependency(depends=['test_table_to_dataframe'])
def test_sheet_to_dataframe():
    st_1_df = sheet_1.to_dataframe()
    print("Result DataFrame:")
    print(st_1_df)
    print("Expected DataFrame:")
    print(sheet_1_df)
    assert st_1_df.equals(sheet_1_df), "Failed to correctly populate dataframe from a sheet"