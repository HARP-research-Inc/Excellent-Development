import openpyxl
import json

def excel_to_json(excelFilePath, jsonFilePath):
    # Load workbook
    wb = openpyxl.load_workbook(excelFilePath)

    # Select the first sheet
    sheet = wb.worksheets[0]

    # Create a dictionary to hold our data
    data = {}

    # Get the column headers (stored in the fourth row of the sheet)
    headers = [cell.value for cell in sheet[4]]

    # Iterate over all rows in the sheet, starting from the fifth row
    for row in sheet.iter_rows(min_row=5, values_only=False):
        # Get the row header (stored in the first column of each row)
        row_header = row[0].value

        # Skip if the row header is null
        if row_header is None:
            continue

        # Create a dictionary to store data for this row
        row_data = {}

        # Iterate over all cells in the row, starting from the second column
        for header, cell in zip(headers[1:], row[1:]):
            # Skip if the header is null
            if header is None:
                continue
            
            # Store data for this cell
            row_data[header] = {
                "value": cell.value,
                "has_formula": cell.data_type == 'f',
                "formula": cell.value if cell.data_type == 'f' else None
            }

        # Store data for this row
        data[row_header] = row_data

    # Write our data dictionary to a JSON file
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        json.dump(data, jsonf, indent=4)

# Driver Code
excelFilePath = r'E:\GDrive\Harpers Startup\Excellent-Development\Book2.xlsx'
jsonFilePath = r'Book_2_example.json'

# Call the excel_to_json function
print(excel_to_json(excelFilePath, jsonFilePath))
