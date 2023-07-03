import openai
import json
import random

openai.api_key = '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'

def generate_synthetic_data(num_examples):
    synthetic_data = []
    chunk_index = 0
    for _ in range(num_examples):
        # Generate a random spreadsheet chunk
        print(f"{chunk_index}: Generating Chunk")
        chunk = generate_random_chunk()
        print(f"{chunk_index}: Chunk: {chunk}")


        # Use OpenAI's API to generate labels for each cell in the chunk
        print(f"{chunk_index}: Labeling Chunk")
        labels = generate_labels_with_openai(chunk)

        # Add the chunk and its labels to the synthetic data
        synthetic_data.append({"chunk": chunk, "labels": labels})

    return synthetic_data
def generate_random_chunk():
    # This function should generate a random spreadsheet chunk as a string
    # The chunk size is randomly chosen between 2x2 and 6x6 cells

    chunk_size = random.randint(2,  6)
    context_size = random.randint(1, 3)  # context size can vary as well

    cells = []
    for _ in range(chunk_size + context_size):
        row = []
        last_was_label = False
        for _ in range(chunk_size + context_size):
            prob = random.random()
            if last_was_label:
                prob += 0.5
            if prob < 0.1:
                # 10% chance to generate an empty cell
                row.append('')
                last_was_label = False
            elif prob < 0.2 :
                # 30% chance to generate a label, or if the last cell was a label
                response = openai.Completion.create(
                  engine="text-davinci-003",
                  prompt="You are a helpful assistant that generates very random labels for cells in a spreadsheet. \n ###User: Generate a simple label for a spreadsheet cell. Please only respond with a the label. \n ###AI: Cashflow \n ###User: Generate a simple label for a spreadsheet cell. Please only respond with a the label. \n ###AI: Item Name \n ###User: Generate a simple label for a spreadsheet cell. Please only respond with a the label. \n ###AI:",
                  temperature=1,
                  max_tokens=3
                )
                label_word = response.choices[0].text.strip()
                print(response.choices[0].text)
                row.append(label_word)
                last_was_label = True
            elif prob < 0.8:
                # 50% chance to generate a number
                row.append(str(random.randint(1, 100)))
                last_was_label = False
            else:
                # 20% chance to generate a formula
                row.append(f"={random.randint(1, 50)}+{random.randint(1, 50)}")
                last_was_label = False
        cells.append(row)

    return cells


def generate_labels_with_openai(chunk):
    for i , row in enumerate(chunk):
        for j, cell in enumerate(row):
            # Surround each cell with ** for highlighting
            highlighted_chunk = [[f"<{c}>" if row_index==i and col_index==j else c 
                                  for col_index, c in enumerate(r)] 
                                 for row_index, r in enumerate(chunk)]
            chunk_str = '\n'.join([','.join(r) for r in highlighted_chunk])
            try:
                if '=' == cell[0]:
                    continue
            except:
                if '' == cell:
                    continue
            # Create the prompt
            prompt=f"""
You are a helpful assistant that determines if cells in a spreadsheet chunk are headers for rows and columns.

###User: Here is a spreadsheet chunk:
<csv>
    <row>
        <cell>
            'Product'
        <cell>
            'Price'
        <cell>
            'Discount'
        <cell>
            'Sale Price'
    <row>
        <cell>
            'Apple'
        <cell>
            '2.50'
        <cell>
            ''
        <cell>
            '=B2'
        <cell>
            ''
    <row>
        <cell>
            Banana'
        <cell>
            '1.20'
        {{selected}}<cell>
            '0.20'
        <cell>
            '=B3-C3'
        <cell>
            ''
    <row>
        <cell>
            'Orange'
        <cell>
            ''
        <cell>
            '0.50'
        <cell>
            '=C4'
        <cell>
            ''
    <row>
        <cell>
            'Grapes'
        <cell>
            '3.75'
        <cell>
            '0.25'
        <cell>
            '=B5-C5'
        <cell>
            '']]
Is the selected cell a header?
###AI: no

###User: Here is a spreadsheet chunk:
[['Month'
        <cell>
            'Sales'
        <cell>
            'Expenses'
        <cell>
            'Profit']
        <cell>
            ['January'
        <cell>
            '2500'
        <cell>
            '1800'
        <cell>
            '=B2-C2'
        <cell>
            '']
        <cell>
            ['February'
        <cell>
            ''
        <cell>
            '2000'
        <cell>
            '=C3'
        <cell>
            '']
        <cell>
            ['March'
        <cell>
            '3500'
        <cell>
            ''
        <cell>
            '=B4'
        <cell>
            '']
        <cell>
            ['April'
        <cell>
            '4000'
        <cell>
            '2500'
        <cell>
            '=B5-C5'
        <cell>
            '']
        <cell>
            ['May'
        <cell>
            '<5500>'
        <cell>
            '3200'
        <cell>
            '=B6-C6'
        <cell>
            '']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[['Category'
        <cell>
            'Item'
        <cell>
            'Quantity'
        <cell>
            'Price'
        <cell>
            'Total']
        <cell>
            ['Electronics'
        <cell>
            'Laptop'
        <cell>
            '2'
        <cell>
            '1200'
        <cell>
            '=C2D2'
        <cell>
            '']
        <cell>
            ['Grocery'
        <cell>
            'Bread'
        <cell>
            '3'
        <cell>
            '2.50'
        <cell>
            '=C3D3'
        <cell>
            '']
        <cell>
            ['Electronics'
        <cell>
            'Phone'
        <cell>
            ''
        <cell>
            '800'
        <cell>
            '=C4D4'
        <cell>
            '']
        <cell>
            ['Grocery'
        <cell>
            '<Milk>'
        <cell>
            '1'
        <cell>
            '1.20'
        <cell>
            '=C5D5'
        <cell>
            '']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[['Name'
        <cell>
            'Age'
        <cell>
            'Gender'
        <cell>
            'Occupation']
        <cell>
            ['John Doe'
        <cell>
            '35'
        <cell>
            ''
        <cell>
            'Software Engineer']
        <cell>
            ['Jane Smith'
        <cell>
            '28'
        <cell>
            'Female'
        <cell>
            'Marketing Manager']
        <cell>
            ['Michael Johnson'
        <cell>
            '<42>'
        <cell>
            'Male'
        <cell>
            'Sales Representative']
        <cell>
            ['Amy Brown'
        <cell>
            '45'
        <cell>
            'Female'
        <cell>
            'Teacher']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[['Country'
        <cell>
            'Population'
        <cell>
            'Area'
        <cell>
            'GDP']
        <cell>
            ['USA'
        <cell>
            '328.2'
        <cell>
            '9.83 million sq km'
        <cell>
            '$22.68 trillion']
        <cell>
            ['China'
        <cell>
            '<1.4 billion>'
        <cell>
            '9.6 million sq km'
        <cell>
            '$17.72 trillion']
        <cell>
            ['India'
        <cell>
            '1.37 billion'
        <cell>
            '3.29 million sq km'
        <cell>
            '$3.17 trillion']
        <cell>
            ['Russia'
        <cell>
            '144 million'
        <cell>
            '17.1 million sq km'
        <cell>
            '$1.64 trillion']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[['Name'
        <cell>
            'Age'
        <cell>
            'Gender'
        <cell>
            'Occupation']
        <cell>
            ['John Doe'
        <cell>
            '35'
        <cell>
            ''
        <cell>
            'Software Engineer']
        <cell>
            ['Jane Smith'
        <cell>
            '28'
        <cell>
            'Female'
        <cell>
            'Marketing Manager']
        <cell>
            ['Michael Johnson'
        <cell>
            '42'
        <cell>
            'Male'
        <cell>
            'Sales Representative']
        <cell>
            ['Amy Brown'
        <cell>
            '45'
        <cell>
            '<Female>'
        <cell>
            'Teacher']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[['Country'
        <cell>
            'Population'
        <cell>
            'Area'
        <cell>
            'GDP']
        <cell>
            ['USA'
        <cell>
            '328.2'
        <cell>
            '9.83 million sq km'
        <cell>
            '$22.68 trillion']
        <cell>
            ['China'
        <cell>
            '1.4 billion'
        <cell>
            '9.6 million sq km'
        <cell>
            '$17.72 trillion']
        <cell>
            ['India'
        <cell>
            '<1.37 billion>'
        <cell>
            '3.29 million sq km'
        <cell>
            '$3.17 trillion']
        <cell>
            ['Russia'
        <cell>
            '144 million'
        <cell>
            '17.1 million sq km'
        <cell>
            '$1.64 trillion']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[['Product'
        <cell>
            'Price'
        <cell>
            'Quantity'
        <cell>
            'Total']
        <cell>
            ['Apple'
        <cell>
            '1.50'
        <cell>
            '10'
        <cell>
            '=B2C2'
        <cell>
            '']
        <cell>
            ['Banana'
        <cell>
            '0.75'
        <cell>
            '5'
        <cell>
            '=B3C3'
        <cell>
            '']
        <cell>
            ['Orange'
        <cell>
            '<0.90>'
        <cell>
            '8'
        <cell>
            '=B4C4'
        <cell>
            '']
        <cell>
            ['Grapes'
        <cell>
            '2.25'
        <cell>
            '3'
        <cell>
            '=B5C5'
        <cell>
            '']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[['Country'
        <cell>
            'Population'
        <cell>
            'Area'
        <cell>
            'GDP']
        <cell>
            ['USA'
        <cell>
            '328.2'
        <cell>
            '9.83 million sq km'
        <cell>
            '$22.68 trillion']
        <cell>
            ['China'
        <cell>
            '1.4 billion'
        <cell>
            '<9.6 million sq km>'
        <cell>
            '$17.72 trillion']
        <cell>
            ['India'
        <cell>
            '1.37 billion'
        <cell>
            '3.29 million sq km'
        <cell>
            '$3.17 trillion']
        <cell>
            ['Russia'
        <cell>
            '144 million'
        <cell>
            '17.1 million sq km'
        <cell>
            '$1.64 trillion']]
Is the cell inside <> a header?
###AI: yes

###User: Here is a spreadsheet chunk:
[['Product'
        <cell>
            'Price'
        <cell>
            '<Quantity>'
        <cell>
            'Total']
        <cell>
            ['Apple'
        <cell>
            '1.50'
        <cell>
            '10'
        <cell>
            '=B2C2'
        <cell>
            '']
        <cell>
            ['Banana'
        <cell>
            '0.75'
        <cell>
            '5'
        <cell>
            '=B3C3'
        <cell>
            '']
        <cell>
            ['Orange'
        <cell>
            '0.90'
        <cell>
            '8'
        <cell>
            '=B4C4'
        <cell>
            '']
        <cell>
            ['Grapes'
        <cell>
            '2.25'
        <cell>
            '3'
        <cell>
            '=B5C5'
        <cell>
            '']]
Is the cell inside <> a header?
###AI: yes

###User: Here is a spreadsheet chunk:
[['Year'
        <cell>
            'Month'
        <cell>
            'Sales'
        <cell>
            'Expenses'
        <cell>
            'Profit']
        <cell>
            ['2021'
        <cell>
            'January'
        <cell>
            '2500'
        <cell>
            '1800'
        <cell>
            '=C2-D2'
        <cell>
            '']
        <cell>
            ['2021'
        <cell>
            'February'
        <cell>
            ''
        <cell>
            '2000'
        <cell>
            '=D3'
        <cell>
            '']
        <cell>
            ['2022'
        <cell>
            '<March>'
        <cell>
            '3500'
        <cell>
            ''
        <cell>
            '=C4'
        <cell>
            '']
        <cell>
            ['2022'
        <cell>
            'April'
        <cell>
            '4000'
        <cell>
            '2500'
        <cell>
            '=C5-D5'
        <cell>
            '']
        <cell>
            ['2022'
        <cell>
            'May'
        <cell>
            '5500'
        <cell>
            '3200'
        <cell>
            '=C6-D6'
        <cell>
            '']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[['Product'
        <cell>
            'Price'
        <cell>
            'Discount'
        <cell>
            'Sale Price']
        <cell>
            ['Apple'
        <cell>
            '2.50'
        <cell>
            ''
        <cell>
            '=B2'
        <cell>
            '']
        <cell>
            ['Banana'
        <cell>
            '1.20'
        <cell>
            '<0.20>'
        <cell>
            '=B3-C3'
        <cell>
            '']
        <cell>
            ['Orange'
        <cell>
            '0.75'
        <cell>
            '<0.50>'
        <cell>
            '=B4-C4'
        <cell>
            '']
        <cell>
            ['Grapes'
        <cell>
            '3.50'
        <cell>
            '0.25'
        <cell>
            '=B5-C5'
        <cell>
            '']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[['Category'
        <cell>
            'Item'
        <cell>
            'Quantity'
        <cell>
            'Price'
        <cell>
            'Total']
        <cell>
            ['Electronics'
        <cell>
            'Laptop'
        <cell>
            '2'
        <cell>
            '1200'
        <cell>
            '=C2D2'
        <cell>
            '']
        <cell>
            ['Grocery'
        <cell>
            'Bread'
        <cell>
            '3'
        <cell>
            '<2.50>'
        <cell>
            '=C3D3'
        <cell>
            '']
        <cell>
            ['Electronics'
        <cell>
            'Phone'
        <cell>
            '1'
        <cell>
            '800'
        <cell>
            '=C4D4'
        <cell>
            '']
        <cell>
            ['Grocery'
        <cell>
            'Milk'
        <cell>
            '1'
        <cell>
            '1.20'
        <cell>
            '=C5D5'
        <cell>
            '']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[[''
        <cell>
            'Q1'
        <cell>
            'Q2'
        <cell>
            'Q3'
        <cell>
            'Q4']
        <cell>
            ['Revenue'
        <cell>
            '5000'
        <cell>
            '6000'
        <cell>
            '5500'
        <cell>
            '7000']
        <cell>
            ['Expenses'
        <cell>
            '<4000>'
        <cell>
            '4500'
        <cell>
            '5000'
        <cell>
            '5500']
        <cell>
            ['Profit'
        <cell>
            '=B2-B3'
        <cell>
            '=C2-C3'
        <cell>
            '=D2-D3'
        <cell>
            '=E2-E3']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[[''
        <cell>
            'Q1'
        <cell>
            'Q2'
        <cell>
            'Q3'
        <cell>
            'Q4']
        <cell>
            ['Revenue'
        <cell>
            '<5000>'
        <cell>
            '6000'
        <cell>
            '5500'
        <cell>
            '7000']
        <cell>
            ['Expenses'
        <cell>
            '4000'
        <cell>
            '4500'
        <cell>
            '5000'
        <cell>
            '5500']
        <cell>
            ['Profit'
        <cell>
            '=B2-B3'
        <cell>
            '=C2-C3'
        <cell>
            '=D2-D3'
        <cell>
            '=E2-E3']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[[''
        <cell>
            'Q1'
        <cell>
            'Q2'
        <cell>
            'Q3'
        <cell>
            'Q4']
        <cell>
            ['Revenue'
        <cell>
            '5000'
        <cell>
            '<6000>'
        <cell>
            '5500'
        <cell>
            '7000']
        <cell>
            ['Expenses'
        <cell>
            '4000'
        <cell>
            '4500'
        <cell>
            '5000'
        <cell>
            '5500']
        <cell>
            ['Profit'
        <cell>
            '=B2-B3'
        <cell>
            '=C2-C3'
        <cell>
            '=D2-D3'
        <cell>
            '=E2-E3']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[[''
        <cell>
            'Q1'
        <cell>
            'Q2'
        <cell>
            'Q3'
        <cell>
            'Q4']
        <cell>
            ['Revenue'
        <cell>
            '5000'
        <cell>
            '6000'
        <cell>
            '<5500>'
        <cell>
            '7000']
        <cell>
            ['Expenses'
        <cell>
            '4000'
        <cell>
            '4500'
        <cell>
            '5000'
        <cell>
            '5500']
        <cell>
            ['Profit'
        <cell>
            '=B2-B3'
        <cell>
            '=C2-C3'
        <cell>
            '=D2-D3'
        <cell>
            '=E2-E3']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[[''
        <cell>
            'Q1'
        <cell>
            'Q2'
        <cell>
            'Q3'
        <cell>
            'Q4']
        <cell>
            ['Revenue'
        <cell>
            '5000'
        <cell>
            '6000'
        <cell>
            '5500'
        <cell>
            '<7000>']
        <cell>
            ['Expenses'
        <cell>
            '4000'
        <cell>
            '4500'
        <cell>
            '5000'
        <cell>
            '5500']
        <cell>
            ['Profit'
        <cell>
            '=B2-B3'
        <cell>
            '=C2-C3'
        <cell>
            '=D2-D3'
        <cell>
            '=E2-E3']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[[''
        <cell>
            'Q1'
        <cell>
            'Q2'
        <cell>
            'Q3'
        <cell>
            'Q4']
        <cell>
            ['Revenue'
        <cell>
            '5000'
        <cell>
            '6000'
        <cell>
            '5500'
        <cell>
            '7000']
        <cell>
            ['Expenses'
        <cell>
            '<4000>'
        <cell>
            '4500'
        <cell>
            '5000'
        <cell>
            '5500']
        <cell>
            ['Profit'
        <cell>
            '=B2-B3'
        <cell>
            '=C2-C3'
        <cell>
            '=D2-D3'
        <cell>
            '=E2-E3']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[[''
        <cell>
            'Q1'
        <cell>
            'Q2'
        <cell>
            'Q3'
        <cell>
            'Q4']
        <cell>
            ['Revenue'
        <cell>
            '5000'
        <cell>
            '6000'
        <cell>
            '5500'
        <cell>
            '7000']
        <cell>
            ['Expenses'
        <cell>
            '4000'
        <cell>
            '<4500>'
        <cell>
            '5000'
        <cell>
            '5500']
        <cell>
            ['Profit'
        <cell>
            '=B2-B3'
        <cell>
            '=C2-C3'
        <cell>
            '=D2-D3'
        <cell>
            '=E2-E3']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[[''
        <cell>
            'Q1'
        <cell>
            'Q2'
        <cell>
            'Q3'
        <cell>
            'Q4']
        <cell>
            ['Revenue'
        <cell>
            '5000'
        <cell>
            '6000'
        <cell>
            '5500'
        <cell>
            '7000']
        <cell>
            ['Expenses'
        <cell>
            '4000'
        <cell>
            '4500'
        <cell>
            '<5000>'
        <cell>
            '5500']
        <cell>
            ['Profit'
        <cell>
            '=B2-B3'
        <cell>
            '=C2-C3'
        <cell>
            '=D2-D3'
        <cell>
            '=E2-E3']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[[''
        <cell>
            'Q1'
        <cell>
            'Q2'
        <cell>
            'Q3'
        <cell>
            'Q4']
        <cell>
            ['Revenue'
        <cell>
            '5000'
        <cell>
            '6000'
        <cell>
            '5500'
        <cell>
            '7000']
        <cell>
            ['Expenses'
        <cell>
            '4000'
        <cell>
            '4500'
        <cell>
            '5000'
        <cell>
            '<5500>']
        <cell>
            ['Profit'
        <cell>
            '=B2-B3'
        <cell>
            '=C2-C3'
        <cell>
            '=D2-D3'
        <cell>
            '=E2-E3']]
Is the cell inside <> a header?
###AI: no

###User: Here is a spreadsheet chunk:
[[''
        <cell>
            'Q1'
        <cell>
            'Q2'
        <cell>
            'Q3'
        <cell>
            'Q4']
        <cell>
            ['Revenue'
        <cell>
            '5000'
        <cell>
            '6000'
        <cell>
            '5500'
        <cell>
            '7000']
        <cell>
            ['Expenses'
        <cell>
            '4000'
        <cell>
            '4500'
        <cell>
            '5000'
        <cell>
            '5500']
        <cell>
            ['<Profit>'
        <cell>
            '=B2-B3'
        <cell>
            '=C2-C3'
        <cell>
            '=D2-D3'
        <cell>
            '=E2-E3']]
Is the cell inside <> a header?
###AI: yes

###User: Here is a spreadsheet chunk:
[[''
        <cell>
            'Q1'
        <cell>
            'Q2'
        <cell>
            'Q3'
        <cell>
            'Q4']
        <cell>
            ['Revenue'
        <cell>
            '5000'
        <cell>
            '6000'
        <cell>
            '5500'
        <cell>
            '7000']
        <cell>
            ['Expenses'
        <cell>
            '4000'
        <cell>
            '4500'
        <cell>
            '5000'
        <cell>
            '5500']
        <cell>
            ['Profit'
        <cell>
            '=B2-B3'
        <cell>
            '<=C2-C3>'
        <cell>
            '=D2-D3'
        <cell>
            '=E2-E3']]
Is the cell inside <> a header?
###AI: no

###User:Here is a spreadsheet chunk:\n\n{chunk_str}\n\nIs the cell inside <> a header?
###AI:"""

            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    temperature=0,
                    max_tokens=3
                )

                # Extract the generated text
                answer = response.choices[0].text.strip().lower()

                # Check if the cell is a label or not
                if 'yes' in answer:
                    chunk[i][j] = "-YES-"+f" {cell}"
                    print(f"Cell:{i}-{j}: {cell} LABEL")
                else:
                    chunk[i][j] = "-NO-"+f" {cell}"
                    print(f"Cell:{i}-{j}: {cell} NONLABEL")

            except Exception as e:
                print(f"Error in generate_labels_with_openai: {e}")

    return chunk

def main():
    synthetic_data = generate_synthetic_data(100)

    # Save the synthetic data to a JSON file
    with open("synthetic_data.json"
        <cell>
            "w") as f:
        json.dump(synthetic_data
        <cell>
            f)

if __name__ == "__main__":
    main()
