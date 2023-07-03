import csv
import json
from tabulate import tabulate
from io import StringIO

def format_cell(cell):
    return f"{{{cell}}}"

def format_chunk(chunk, annotated_output):
    formatted_chunks = []
    for row_idx, row in enumerate(chunk):
        for col_idx, cell in enumerate(row):
            # Skip if the cell doesn't contain actual data
            if cell[0] == ' ' or cell[1].startswith('='):
                continue
            formatted_row = [f"[TYPE={annotated_output[cell[0]]}], {cell[1]}" if cell[0] in annotated_output else cell for cell in row]
            formatted_row[col_idx] = f"{{{formatted_row[col_idx]}}}"
            formatted_chunk = [formatted_row if idx == row_idx else row_item for idx, row_item in enumerate(chunk)]
            si = StringIO()
            cw = csv.writer(si)
            cw.writerows(formatted_chunk)
            formatted_chunks.append((si.getvalue().strip(), cell[0]))
    return formatted_chunks

def extract_chunks_from_file(file_path='output.json', annotated_output=None):
    if annotated_output is None:
        annotated_output = {}

    with open(file_path, 'r') as file:
        output_dict = json.load(file)

    chunks = []
    for sheet_value in output_dict.values():
        for row_value in sheet_value.values():
            for chunk_value in row_value.values():
                chunks.append(format_chunk(chunk_value['base_chunk'], annotated_output))
                
    return chunks


def print_highlighted_chunks(chunks):
    for chunk_group in chunks:
        for i, chunk_str in enumerate(chunk_group):
            reader = csv.reader(StringIO(chunk_str))
            chunk = list(reader)
            print(f"Highlighted Cell {i+1}:\n")
            print(tabulate(chunk, tablefmt="fancy_grid", numalign="left"))
            print("\n")
            
def annotate_cells(file_path='output.json'):
    annotated_output = {}

    while True:
        chunks = extract_chunks_from_file(file_path, annotated_output)
        all_annotated = True
        for chunk_group in chunks:
            for chunk_str, cell_id in chunk_group:
                # If cell already annotated, skip
                if cell_id in annotated_output:
                    continue
                all_annotated = False

                reader = csv.reader(StringIO(chunk_str))
                chunk = list(reader)
                print(f"Highlighted Cell {cell_id}:\n")
                print(tabulate(chunk, tablefmt="fancy_grid", numalign="left"))
                print("\n")

                # Prompt user for input
                label_cell = input(f"Is cell {cell_id} a label cell? (Y/N) ")
                if label_cell.lower() == 'y':
                    annotated_output[cell_id] = 'LABEL'
        if all_annotated:
            break

    # Write annotated output to JSON file
    with open('annotated_output.json', 'w') as f:
        json.dump(annotated_output, f, indent=4)

    print("Finished annotating cells.")

chunks = annotate_cells()
print_highlighted_chunks(chunks)
