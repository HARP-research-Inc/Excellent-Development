import json
import csv
from io import StringIO
from tabulate import tabulate
from nltk.tokenize import word_tokenize
from itertools import zip_longest


def import_conversations_from_json(file_path):
    with open(file_path, 'r') as file:
        conversations = json.load(file)
    csv_datas = [entry['assistant'].strip('```').strip() for entry in conversations]
    return csv_datas

def generate_keys(num_rows, num_cols):
    return [chr(ord('A') + col) + str(row + 1) for row in range(num_rows) for col in range(num_cols)]

def cut_csv_into_chunks(csv_data, chunk_size, context_size):
    reader = csv.reader(StringIO(csv_data))
    data = list(reader)
    max_row_length = max(len(row) for row in data)
    data = [
        [
            (
                (f'{chr(65 + col_idx)}{row_idx + 1}', cell)
                if cell != ''
                else (f'{chr(65 + col_idx)}{row_idx + 1}', ' ')
            )
            for col_idx, cell in enumerate(row + [' '] * (max_row_length - len(row)))
        ]
        for row_idx, row in enumerate(data)
    ]
    num_rows = len(data)
    num_cols = max_row_length
    num_row_chunks = -(-num_rows // chunk_size)  # Ceiling division
    num_col_chunks = -(-num_cols // chunk_size)  # Ceiling division
    chunked_rows = [
        [
            {
                'chunk': [
                    row[start_col:end_col]
                    for row in data[start_row:end_row]
                ],
                'row_context': [
                    row[start_col:end_col]
                    for row in data[max(start_row - context_size, 0):start_row]
                ] if i > 0 else [],
                'col_context': [
                    row[max(start_col - context_size, 0):start_col]
                    for row in data[start_row:end_row]
                ] if j > 0 else []
            }
            for j in range(num_col_chunks)
            for start_col, end_col in [
                (j * chunk_size, min((j + 1) * chunk_size, num_cols))
            ]
            for start_row, end_row in [
                (i * chunk_size, min((i + 1) * chunk_size, num_rows))
            ]
        ]
        for i in range(num_row_chunks)
    ]
    return chunked_rows

def join_with_proper_alignment(list1, list2):
    return list1 or list2 or [b + a for a, b in zip_longest(list1, list2, fillvalue=[('', ' ')] * len(list1[0]))]

def concat_with_empty_rows(list1, list2):
    if not list1:
        return list2
    if not list2:
        return list1

    len_diff = len(list2[0]) - len(list1[0])
    if len_diff > 0:
        list1 = [([(' ', ' ')] * len_diff) + row for row in list1]
    elif len_diff < 0:
        list2 = [([(' ', ' ')] * -len_diff) + row for row in list2]

    return list1 + list2

import json

def print_output_json(output_json):
    # Load the JSON string into a dictionary
    output_dict = json.loads(output_json)

    # Iterate over sheets
    for sheet_key, sheet_value in output_dict.items():
        print(f"\n{sheet_key}:\n")

        # Retrieve and print the corresponding CSV data
        csv_data = import_conversations_from_json('JSONs/generated_conversation.json')
        csv_data_index = int(sheet_key.split()[-1]) - 1
        print(csv_data[csv_data_index].replace(',', '\t'))

        # Iterate over rows
        for row_key, row_value in sheet_value.items():
            print(f"\n{row_key}:")

            # Iterate over chunks
            for chunk_key, chunk_value in row_value.items():
                print(f"\n{chunk_key} Base chunk:")
                print(tabulate(chunk_value['base_chunk'], tablefmt="plain", numalign="left"))
                print(f"\n{chunk_key} With Context:")
                print(tabulate(chunk_value['contextualized_chunk'], tablefmt="plain", numalign="left"))
import json

def generate_output_json(file_path, chunk_size, context_size):
    # Load csv_data from json file
    csv_datas = import_conversations_from_json(file_path)

    # Prepare a list to store all sheets
    all_sheets = [cut_csv_into_chunks(data, chunk_size, context_size) for data in csv_datas]

    # Create a dictionary to hold the output
    output_dict = {}

    # Iterate over the chunked data
    for sheet_num, (sheet, csv_data) in enumerate(zip(all_sheets, csv_datas)):
        sheet_dict = {}
        for row_num, row in enumerate(sheet):
            row_dict = {}
            for chunk_num, chunk_info in enumerate(row):
                contined = join_with_proper_alignment(chunk_info['chunk'], chunk_info['col_context'])
                combined = concat_with_empty_rows(chunk_info['row_context'], contined)



                chunk_dict = {
                    "base_chunk": chunk_info['chunk'],
                    "contextualized_chunk": combined,
                    "tokens": len(word_tokenize('\n'.join(['_'.join(str(subitem) for subitem in item) for item in combined])))
                }

                row_dict[f"Chunk {chunk_num+1}"] = chunk_dict

            sheet_dict[f"Row {row_num+1}"] = row_dict

        output_dict[f"Sheet {sheet_num+1}"] = sheet_dict

    # Convert the dictionary to a JSON string
    output_json = json.dumps(output_dict, indent=4)

    # Save the output JSON to a file
    with open('JSONs/output.json', 'w') as file:
        file.write(output_json)

    # Return the output JSON string
    return output_json

def test_func():
    file_path = 'JSONs/generated_conversation.json'
    chunk_size = 5
    context_size = 2
    output_json = generate_output_json(file_path, chunk_size, context_size)
    print_output_json(output_json)