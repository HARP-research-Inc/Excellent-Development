import pandas as pd
from io import StringIO
import json
from gensim.utils import tokenize
import numpy as np
import uuid
import warnings
import csv
warnings.simplefilter(action='ignore', category=FutureWarning)



def import_conversations_from_json(file_path):
    with open(file_path, 'r') as file:
        conversations = json.load(file)
    
    csv_datas = []
    for entry in conversations:
        content = entry['assistant'].strip('```').strip()
        csv_datas.append(content)
    
    return csv_datas


def import_conversations_from_json(file_path):
    with open(file_path, 'r') as file:
        conversations = json.load(file)
    
    csv_datas = []
    for entry in conversations:
        content = entry['assistant'].strip('```').strip()
        csv_datas.append(content)
    
    return csv_datas

import json

def cut_csv_into_chunks(csv_data, chunk_size, context_size):
    # Read the CSV data into a list of lists
    reader = csv.reader(StringIO(csv_data))
    data = list(reader)

    # Determine the maximum row length
    max_row_length = max(len(row) for row in data)

    # Ensure all rows are of uniform length and replace empty cells with ' '
    data = [[cell if cell != '' else ' ' for cell in row + [' '] * (max_row_length - len(row))] for row in data]

    # Get the number of rows and columns in the data
    num_rows = len(data)
    num_cols = max_row_length

    # Calculate the number of chunks needed in each dimension
    num_row_chunks = -(-num_rows // chunk_size)  # Ceiling division
    num_col_chunks = -(-num_cols // chunk_size)  # Ceiling division

    # Initialize a list to store the chunked data
    chunked_rows = []

    # Loop over the chunks and extract each chunk from the data
    for i in range(num_row_chunks):
        chunked_row = []
        for j in range(num_col_chunks):
            start_row = i * chunk_size
            end_row = min((i+1) * chunk_size, num_rows)
            start_col = j * chunk_size
            end_col = min((j+1) * chunk_size, num_cols)
            
            chunk = [row[start_col:end_col] for row in data[start_row:end_row]]
            row_context = [row[start_col:end_col] for row in data[max(start_row-context_size, 0):start_row]] if i > 0 else []
            col_context = [row[max(start_col-context_size, 0):start_col] for row in data[start_row:end_row]] if j > 0 else []
            
            # Convert chunks to dictionary
            chunk_dict = {
                'chunk': chunk,
                'row_context': row_context,
                'col_context': col_context
            }
            chunked_row.append(chunk_dict)

        chunked_rows.append(chunked_row)

    # Return the list of chunked rows
    return chunked_rows

# Load csv_data from json file
csv_datas = import_conversations_from_json('JSONs/generated_conversation.json')

# Prepare a list to store all sheets
all_sheets = []

for data in csv_datas:
    # Cut the data into chunked rows
    chunked_rows = cut_csv_into_chunks(data, 5, 2)
    all_sheets.append(chunked_rows)

# Convert chunked DataFrames into JSON and save
with open('chunked_sheet.json', 'w') as file:
    json.dump(all_sheets, file)

# Load csv_data from json file
csv_datas = import_conversations_from_json('JSONs/generated_conversation.json')

# Prepare a list to store all sheets
all_sheets = []

for data in csv_datas:
    # Cut the data into chunked rows
    chunked_rows = cut_csv_into_chunks(data, 5, 2)
    all_sheets.append(chunked_rows)

from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')

# Function to join DataFrames with different number of columns by adding empty columns if needed
def join_with_proper_alignment(df1, df2):
    # Ensuring the dataframes have the same number of rows
    if df1.shape[0] < df2.shape[0]:
        empty_df = pd.DataFrame('', index=range(df2.shape[0] - df1.shape[0]), columns=df1.columns)
        df1 = pd.concat([df1, empty_df], axis=0).reset_index(drop=True)
    elif df1.shape[0] > df2.shape[0]:
        empty_df = pd.DataFrame('', index=range(df1.shape[0] - df2.shape[0]), columns=df2.columns)
        df2 = pd.concat([df2, empty_df], axis=0).reset_index(drop=True)

    # Now, we can join the dataframes horizontally
    return pd.concat([df1, df2], axis=1)

def concat_with_empty_rows(df2, df1):
    # Resetting index and converting dataframes to dictionaries
    dict1 = df1.reset_index(drop=True).to_dict(orient='list')
    dict2 = df2.reset_index(drop=True).to_dict(orient='list')
    dict3 = {}

    # print(f"\ndict1:\n{dict1}\n\ndict2:\n{dict2}\n")
    # Combining two dictionaries
    lenval = 0
    for i in dict2.values():
        if len(i) > lenval:
            lenval = len(i)

    for i in dict1.keys():
        if (i in dict2.keys()):
            dict3[i]=dict2[i]
        else:
            list_i=[]
            for j in range(lenval):
                list_i.append('')
            dict3[i] = list_i
        #print(len(dict3[i]))

    # print(f"\ndict3:\n{dict3}")
    combined_dict = {}
    for i in dict1.keys():
        list_i =[]
        for j in dict3[i]:
            list_i.append(j)
        for j in dict1[i]:
            list_i.append(j)
        #print(len(list_i))
        combined_dict[i]=list_i
    # print(f"\ncombined_dict:\n{combined_dict}\n")
    # Convert combined_dict to DataFrame
    combined_df = pd.DataFrame(combined_dict)

    return combined_df


# Print the chunked DataFrames
for sheet_num, sheet in enumerate(all_sheets):
    print(f"Sheet {sheet_num+1}:")
    print(f"Rows: {len(sheet)}")
    print(csv_datas[sheet_num])
    for row_num, row in enumerate(sheet):
        print(f"\nRow {row_num+1}:")
        for chunk_num, chunk_info in enumerate(row):
            # Convert dictionary to DataFrame
            chunk_df = pd.DataFrame.from_dict(chunk_info['chunk'])
            row_context_df = pd.DataFrame.from_dict(chunk_info['row_context'])
            col_context_df = pd.DataFrame.from_dict(chunk_info['col_context'])

            print(f"Chunk {chunk_num+1}:\nData chunk: {chunk_df.to_string(index=False, header=False)}")
            # Concatenate the result with column context
            combined_df = join_with_proper_alignment(col_context_df, chunk_df)
            #print(f"Add Column: {combined_df.to_string(index=False, header=False)}")
            # Concatenate row context and chunk
            combined_df = concat_with_empty_rows(row_context_df, combined_df) 
            print(f"\nAdded Column and Row: \n{combined_df.to_string(index=False, header=False)}")

            chunk_string = f"""Chunk {chunk_num+1}:
Data chunk: \n
{chunk_df.to_string(header=False, index=False)}

Row context:
{row_context_df.to_string(header=False, index=False) if not row_context_df.empty else ''}

Column context:
{col_context_df.to_string(header=False, index=False) if not col_context_df.empty else ''}
"""
            print(f"\nChunk {chunk_num+1} tokens: "+str(len(word_tokenize(chunk_string))))



"""Chunk 1 tokens: 54
Chunk 2:
Data chunk:
Misalignment 8 Repair
     Scratch 7 Repair
     Scratch 7 Repair
Misalignment 8 Reject

Add Column:
02/03/2021 Line 3 Misalignment 8 Repair
02/03/2021 Line 4      Scratch 7 Repair
02/04/2021 Line 1      Scratch 7 Repair
02/04/2021 Line 2 Misalignment 8 Reject

Add Row:
Misalignment 8 Repair 02/03/2021 Line 3
     Scratch 7 Repair 02/03/2021 Line 4
     Scratch 7 Repair 02/04/2021 Line 1
Misalignment 8 Reject 02/04/2021 Line 2
     Scratch 6 Repair
       Crack 9 Reject
       
when I want
 
Chunk 1 tokens: 54
Chunk 2:
Data chunk:
Misalignment 8 Repair
     Scratch 7 Repair
     Scratch 7 Repair
Misalignment 8 Reject

Add Column:
02/03/2021 Line 3 Misalignment 8 Repair
02/03/2021 Line 4      Scratch 7 Repair
02/04/2021 Line 1      Scratch 7 Repair
02/04/2021 Line 2 Misalignment 8 Reject

Add Row:
                       Scratch 6 Repair
                         Crack 9 Reject
02/03/2021 Line 3 Misalignment 8 Repair
02/03/2021 Line 4      Scratch 7 Repair
02/04/2021 Line 1      Scratch 7 Repair
02/04/2021 Line 2 Misalignment 8 Reject
"""