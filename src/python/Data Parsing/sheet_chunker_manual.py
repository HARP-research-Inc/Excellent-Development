import json
import csv
from io import StringIO
from tabulate import tabulate
from nltk.tokenize import word_tokenize
import nltk
#nltk.download('punkt')
from itertools import zip_longest


def import_conversations_from_json(file_path):
    with open(file_path, 'r') as file:
        conversations = json.load(file)
    
    csv_datas = []
    for entry in conversations:
        content = entry['assistant'].strip('```').strip()
        csv_datas.append(content)
    
    return csv_datas

def generate_keys(num_rows, num_cols):
    # Create a list to store the keys
    keys = []

    # Create keys for each cell
    for row in range(num_rows):
        for col in range(num_cols):
            # Convert the column index to a letter
            letter = chr(ord('A') + col)

            # Create the key and append it to the list
            key = letter + str(row + 1)
            keys.append(key)

    # Return the list of keys
    return keys

def cut_csv_into_chunks(csv_data, chunk_size, context_size):
    # Read the CSV data into a list of lists
    reader = csv.reader(StringIO(csv_data))
    data = list(reader)

    # Determine the maximum row length
    max_row_length = max(len(row) for row in data)

    # Ensure all rows are of uniform length and replace empty cells with a placeholder tuple
    data = [[(f'{chr(65 + col_idx)}{row_idx + 1}', cell) if cell != '' else ((f'{chr(65 + col_idx)}{row_idx + 1}', ' ')) 
             for col_idx, cell in enumerate(row + [' '] * (max_row_length - len(row)))] for row_idx, row in enumerate(data)]

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
            # Determine the row context based on the current index (i)
            if i > 0:
                # If the current index is greater than 0, extract the row context
                start_row_context = max(start_row - context_size, 0)  # Calculate the starting row index for the context
                end_row_context = start_row  # Calculate the ending row index for the context
                row_context = [row[start_col:end_col] for row in data[start_row_context:end_row_context]]
            else:
                # If the current index is 0, there is no row context
                row_context = []

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

def join_with_proper_alignment(list1, list2):
    if not list1 or not list2:
        # Return the non-empty list or an empty list if both are empty
        return list1 or list2
    else:
        return [b + a for a, b in zip_longest(list1, list2, fillvalue=[('', ' ')] * len(list1[0]))]


def concat_with_empty_rows(list1, list2):
    print(f'row context: \n{tabulate(list1, tablefmt="plain", numalign="left")}')
    if not list1:
        return list2
    if not list2:
        return list1

    len_diff = len(list2[0]) - len(list1[0])
    print(f"len_diff: {len_diff}")
    if len_diff > 0:
        # Add empty elements to list1
        for i, row in enumerate(list1):
            new_elements = [(' ', ' ')] * len_diff
            list1[i] =  new_elements + row
    elif len_diff < 0:
        # Add empty elements to list2
        for i, row in enumerate(list2):
            new_elements = [(' ', ' ')] * -len_diff
            list2[i] = new_elements + row


    return list1 + list2
def output_func():
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

    # Create a dictionary to hold the output
    output_dict = {}

    # Iterate over the chunked data
    for sheet_num, sheet in enumerate(all_sheets):
        print(f"\nSheet {sheet_num+1}:\n")
        print(csv_datas[sheet_num].replace(',', '\t'))  # print the sheet as a tab-separated table
        sheet_dict = {}
        for row_num, row in enumerate(sheet):
            row_dict = {}
            print(f"Row: {row_num+1}")
            for chunk_num, chunk_info in enumerate(row):
                # Concatenate the result with column context
                contined = join_with_proper_alignment(chunk_info['chunk'], chunk_info['col_context'])

                # Concatenate row context and chunk
                combined = concat_with_empty_rows(chunk_info['row_context'], contined)


                # Create a dictionary for the chunk
                chunk_dict = {
                    "Data chunk": chunk_info['chunk'],
                    "Added Column and Row Context": combined,
                    "Tokens": len(word_tokenize('\n'.join(['_'.join(str(subitem) for subitem in item) for item in combined]))),
                }

                # Print each data chunk and combined context as a tab-separated table

                print(f"\nChunk {chunk_num+1} Data chunk:\n")
                print(tabulate(chunk_dict['Data chunk'], tablefmt="plain", numalign="left"))
                print(f"\nChunk {chunk_num+1} Added Column Context:\n")
                print(tabulate(contined, tablefmt="plain", numalign="left"))
                print()
                combined = concat_with_empty_rows(chunk_info['row_context'], contined)
                print(f"\nChunk {chunk_num+1} Added Row Context:\n")
                print(tabulate(chunk_dict['Added Column and Row Context'], tablefmt="plain", numalign="left"))

                # Add the chunk dictionary to the row dictionary
                row_dict[f"Chunk {chunk_num+1}"] = chunk_dict

            # Add the row dictionary to the sheet dictionary
            sheet_dict[f"Row {row_num+1}"] = row_dict

        # Add the sheet dictionary to the output dictionary
        output_dict[f"Sheet {sheet_num+1}"] = sheet_dict

    # Convert the dictionary to a JSON string and print it in a readable format
    output_json = json.dumps(output_dict, indent=4)
    print("\nOutput JSON:")
    #print(output_json)

"""
Chunk 2 Added Column Context:

('F4', ' ')                 ('G4', ' ')   ('D6', 'In Progress')  ('E6', '09/01/2023')
('F5', 'Completion Date')   ('G5', ' ')   ('D7', 'Not Started')  ('E7', '08/20/2023')
('F6', ' ')                 ('G6', ' ')   ('D8', 'Completed')    ('E8', '08/14/2023')
('F7', ' ')                 ('G7', ' ')   ('D9', ' ')            ('E9', ' ')
('F8', '08/14/2023')        ('G8', ' ')   ('D10', 'Status')      ('E10', 'Due Date')
('F9', ' ')                 ('G9', ' ')   ('', ' ')              ('', ' ')
('F10', 'Completion Date')  ('G10', ' ')  ('', ' ')              ('', ' ')


Chunk 2 Added Row Context:

('', ' ')              ('', ' ')                ('F4', ' ')                 ('G4', ' ')   
('', ' ')              ('', ' ')                ('F5', 'Completion Date')   ('G5', ' ')   
('D6', 'In Progress')  ('E6', '09/01/2023')     ('F6', ' ')                 ('G6', ' ')   
('D7', 'Not Started')  ('E7', '08/20/2023')     ('F7', ' ')                 ('G7', ' ')   
('D8', 'Completed')    ('E8', '08/14/2023')     ('F8', '08/14/2023')        ('G8', ' ')   
('D9', ' ')            ('E9', ' ')              ('F9', ' ')                 ('G9', ' ')   
('D10', 'Status')      ('E10', 'Due Date')      ('F10', 'Completion Date')  ('G10', ' ')  



Chunk 2 Data chunk:

('F11', ' ')           ('G11', ' ')
('F12', ' ')           ('G12', ' ')
('F13', '08/11/2023')  ('G13', ' ')

Chunk 2 Added Column Context:

('F11', ' ')           ('G11', ' ')  ('D11', 'Not Started')  ('E11', '09/01/2023')
('F12', ' ')           ('G12', ' ')  ('D12', 'In Progress')  ('E12', '08/25/2023')
('F13', '08/11/2023')  ('G13', ' ')  ('D13', 'Completed')    ('E13', '08/11/2023')

Chunk 2 Added Row Context:

('F9', ' ')                 ('G9', ' ')   ('C2', ' ')             ('C2', ' ')
('F10', 'Completion Date')  ('G10', ' ')  ('D2', ' ')             ('D2', ' ')
('F11', ' ')                ('G11', ' ')  ('D11', 'Not Started')  ('E11', '09/01/2023')
('F12', ' ')                ('G12', ' ')  ('D12', 'In Progress')  ('E12', '08/25/2023')
('F13', '08/11/2023')       ('G13', ' ')  ('D13', 'Completed')    ('E13', '08/11/2023')


Chunk 2 Data chunk:

('F11', ' ')           ('G11', ' ')
('F12', ' ')           ('G12', ' ')
('F13', '08/11/2023')  ('G13', ' ')

Chunk 2 Added Column Context:

('D11', 'Not Started')  ('E11', '09/01/2023')  ('F11', ' ')           ('G11', ' ')
('D12', 'In Progress')  ('E12', '08/25/2023')  ('F12', ' ')           ('G12', ' ')
('D13', 'Completed')    ('E13', '08/11/2023')  ('F13', '08/11/2023')  ('G13', ' ')

Chunk 2 Added Row Context:

('F9', ' ')                 ('G9', ' ')            ('C2', ' ')            ('C2', ' ')
('F10', 'Completion Date')  ('G10', ' ')           ('D2', ' ')            ('D2', ' ')
('D11', 'Not Started')      ('E11', '09/01/2023')  ('F11', ' ')           ('G11', ' ')
('D12', 'In Progress')      ('E12', '08/25/2023')  ('F12', ' ')           ('G12', ' ')
('D13', 'Completed')        ('E13', '08/11/2023')  ('F13', '08/11/2023')  ('G13', ' ')
"""