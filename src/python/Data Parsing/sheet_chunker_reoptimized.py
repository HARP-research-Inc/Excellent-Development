import json
import csv
import nltk
from io import StringIO
from itertools import zip_longest
from tabulate import tabulate

# Use a generator to yield conversations one at a time
def import_conversations_from_json(file_path):
    with open(file_path, 'r') as file:
        conversations = json.load(file)
    for entry in conversations:
        yield entry['assistant'].strip('```').strip()

# Merge join_with_proper_alignment and concat_with_empty_rows into one
def join_or_concat_with_proper_alignment(list1, list2, action='join'):
    if not list1:
        return list2
    if not list2:
        return list1
    len_diff = len(list2[0]) - len(list1[0])
    if len_diff > 0:
        list1 = [([(' ', ' ')] * len_diff) + row for row in list1]
    elif len_diff < 0:
        list2 = [([(' ', ' ')] * -len_diff) + row for row in list2]
    if action == 'join':
        return [b + a for a, b in zip_longest(list1, list2, fillvalue=[('', ' ')] * len(list1[0]))]
    elif action == 'concat':
        return list1 + list2

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

def generate_output_json(file_path, chunk_size, context_size):
    all_sheets = [cut_csv_into_chunks(data, chunk_size, context_size) for data in import_conversations_from_json(file_path)]
    output_dict = {}
    for sheet_num, sheet in enumerate(all_sheets):
        sheet_dict = {}
        for row_num, row in enumerate(sheet):
            row_dict = {}
            for chunk_num, chunk_info in enumerate(row):
                combined = join_or_concat_with_proper_alignment(chunk_info['row_context'], join_or_concat_with_proper_alignment(chunk_info['chunk'], chunk_info['col_context'], 'join'), 'concat')
                chunk_dict = {
                    "base_chunk": chunk_info['chunk'],
                    "contextualized_chunk": combined,
                }
                row_dict[f"Chunk {chunk_num+1}"] = chunk_dict
            sheet_dict[f"Row {row_num+1}"] = row_dict
        output_dict[f"Sheet {sheet_num+1}"] = sheet_dict
    output_json = json.dumps(output_dict, indent=4)
    with open('output.json', 'w') as file:
        file.write(output_json)
    return output_json

def print_output_json(output_json):
    output_dict = json.loads(output_json)
    csv_data = list(import_conversations_from_json('JSONs/generated_conversation.json'))
    for sheet_key, sheet_value in output_dict.items():
        print(f"\n{sheet_key}:\n")
        csv_data_index = int(sheet_key.split()[-1]) - 1
        print(csv_data[csv_data_index].replace(',', '\t'))
        for row_key, row_value in sheet_value.items():
            print(f"\n{row_key}:")
            for chunk_key, chunk_value in row_value.items():
                print(f"\n{chunk_key} Base chunk:")
                print(tabulate(chunk_value['base_chunk'], tablefmt="plain", numalign="left"))
                print(f"\n{chunk_key} With Context:")
                print(tabulate(chunk_value['contextualized_chunk'], tablefmt="plain", numalign="left"))

def test_func():
    file_path = 'JSONs/generated_conversation.json'
    chunk_size = 5
    context_size = 2
    output_json = generate_output_json(file_path, chunk_size, context_size)
    print_output_json(output_json)

test_func()