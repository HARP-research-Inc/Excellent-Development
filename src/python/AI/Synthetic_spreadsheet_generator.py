import openai
import json
import random

subtable_type = [
    'with horizontal subtables',
    'with veritcal subtables',
    'with subtables',
    '']
header = ['and with a header', '']
spreadsheet_types = [
    "Personal Budget Spreadsheet",
    "Financial Statement Spreadsheet",
    "Expense Tracking Spreadsheet",
    "Inventory Management Spreadsheet",
    "Project Management Spreadsheet",
    "Sales Tracking Spreadsheet",
    "Time Tracking Spreadsheet",
    "Task Management Spreadsheet",
    "Work Schedule Spreadsheet",
    "Employee Timesheet Spreadsheet",
    "Invoice Tracking Spreadsheet",
    "Business Performance Dashboard",
    "Client Database Spreadsheet",
    "Event Planning Spreadsheet",
    "Meal Planning Spreadsheet",
    "Workout Tracking Spreadsheet",
    "Mortgage Calculator Spreadsheet",
    "Retirement Savings Spreadsheet",
    "Student Gradebook Spreadsheet",
    "Travel Itinerary Spreadsheet",
    "Wedding Planning Spreadsheet",
    "Data Analysis Spreadsheet",
    "Product Comparison Spreadsheet",
    "Content Calendar Spreadsheet",
    "Social Media Analytics Spreadsheet",
    "SEO Keyword Research Spreadsheet",
    "Customer Relationship Management (CRM) Spreadsheet",
    "Recruitment Tracker Spreadsheet",
    "Conference Attendee Spreadsheet",
    "Asset Management Spreadsheet",
    "Bug Tracking Spreadsheet",
    "Quality Control Spreadsheet",
    "Risk Assessment Spreadsheet",
    "Investment Portfolio Spreadsheet",
    "Real Estate Analysis Spreadsheet",
    "Grant Proposal Budget Spreadsheet",
    "Research Data Collection Spreadsheet",
    "Survey Results Spreadsheet",
    "Employee Training Tracker Spreadsheet",
    "Donation Tracker Spreadsheet"
]


# Set up your OpenAI API key
openai.api_key = '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'

# Define the conversation
conversation = [
    {'role': 'system', 'content': 'You are a spreadsheet data generation assistant which can generate realistic CSV code to create synthetic datasets. You will reply only in CSV code.'},
    {'role': 'user', 'content': 'Generate a financial spreadsheet example formatted in csv code '},
    {'role': 'assistant', 'content': '''```
Name,Revenue,Expenses,Profit/Loss,Accounts Receivable,Accounts Payable,Inventory
Brokemun,10000,5000,5000,20000,10000,5000
Corplum,12000,6000,6000,22000,11000,6000
IndexTrade,15000,7500,7500,25000,12000,7000
Build Ops Inc.,18000,9000,9000,28000,13000,8000
Chevron,20000,10000,10000,30000,14000,9000
Buildfire,22000,11000,11000,32000,15000,10000
Verizon,24000,12000,12000,34000,16000,11000
Bank of America,26000,13000,13000,36000,17000,12000
Operations Mark,28000,14000,14000,38000,18000,13000
Alphabet Inc.,30000,15000,15000,40000,19000,14000
Truckstop,32000,16000,16000,42000,20000,15000
Forn,35000,17500,17500,45000,21000,16000
```'''},
    {'role': 'user', 'content': 'Generate an accounting spreadsheet example formatted in csv code '},
    {'role': 'assistant', 'content': '''```
Date,Account,Debit,Credit
01/01/2021,Cash,10000,
01/01/2021,Accounts Receivable,,20000
01/01/2021,Sales Revenue,,10000
02/01/2021,Cash,12000,
02/01/2021,Accounts Receivable,,22000
02/01/2021,Sales Revenue,,12000
03/01/2021,Cash,15000,
03/01/2021,Accounts Receivable,,25000
03/01/2021,Sales Revenue,,15000
04/01/2021,Cash,18000,
04/01/2021,Accounts Receivable,,28000
04/01/2021,Sales Revenue,,18000
05/01/2021,Cash,20000,
05/01/2021,Accounts Receivable,,30000
05/01/2021,Sales Revenue,,20000
06/01/2021,Cash,22000,
06/01/2021,Accounts Receivable,,32000
06/01/2021,Sales Revenue,,22000
07/01/2021,Cash,24000,
07/01/2021,Accounts Receivable,,34000
07/01/2021,Sales Revenue,,24000
08/01/2021,Cash,26000,
08/01/2021,Accounts Receivable,,36000
08/01/2021,Sales Revenue,,26000
09/01/2021,Cash,28000,
09/01/2021,Accounts Receivable,,38000
09/01/2021,Sales Revenue,,28000
10/01/2021,Cash,30000,
10/01/2021,Accounts Receivable,,40000
10/01/2021,Sales Revenue,,30000
11/01/2021,Cash,32000,
11/01/2021,Accounts Receivable,,42000
11/01/2021,Sales Revenue,,32000
12/01/2021,Cash,,
12/01/2021,Accounts Receivable,,45000
12/01/2021,Sales Revenue,,35000
12/01/2021,Accounts Payable,17500,
```'''},
    {'role': 'user', 'content': 'Generate an accounting spreadsheet with vertical subtables example formatted in csv code '},
    {'role': 'assistant', 'content': '''```
Date,Transaction,Amount
2023-01-01,Salary,5000
2023-01-02,Rent,-1000
2023-01-03,Groceries,-200
,,,,
Date,Transaction,Amount
2023-02-01,Salary,5000
2023-02-02,Rent,-1000
2023-02-03,Groceries,-300
,,,,
Date,Transaction,Amount
2023-03-01,Salary,5000
2023-03-02,Rent,-1000
2023-03-03,,Groceries,-250
    ```'''},
    {'role': 'user', 'content': 'Generate an accounting spreadsheet with horizontal subtables example formatted in csv code '},
    {'role': 'assistant', 'content': '''```
Date,Transaction,Amount,,,,Date,Transaction,Amount,,,,Date,Transaction,Amount
2023-01-01,Salary,5000,,,,2023-02-01,Salary,5000,,,,2023-03-01,Salary,5000
2023-01-02,Rent,-1000,,,,2023-02-02,Rent,-1000,,,,2023-03-02,Rent,-1000
2023-01-03,Groceries,-200,,,,2023-02-03,Groceries,-300,,,,2023-03-03,Groceries,-250
```'''},
    {'role': 'user', 'content': 'Generate an accounting spreadsheet with subtables example formatted in csv code '},
    {'role': 'assistant', 'content': '''```
Date,Transaction,Amount,,,,Category,Expense,Amount
2023-01-01,Salary,5000,,,,Groceries,-200,500
2023-01-02,Rent,-1000,,,,Utilities,-150,300
2023-01-03,Groceries,-200,,,,Entertainment,-50,150
,,,,,,
Category,Expense,Amount,,,,Date,Transaction,Amount
Groceries,-300,450,,,,2023-02-01,Salary,5000
Utilities,-200,350,,,,2023-02-02,Rent,-1000
Entertainment,-50,300,,,,2023-02-03,Groceries,-300
,,,,,,
Category,Expense,Amount,,,,Date,Transaction,Amount
Groceries,-250,200,,,,2023-03-01,Salary,5000
Utilities,-150,150,,,,2023-03-02,Rent,-1000
Entertainment,-100,50,,,,,
```'''},
    {'role': 'user', 'content': 'Generate an accounting spreadsheet example with verticle subtables and a header formatted in csv code '},
    {'role': 'assistant', 'content': '''```
Company: XYZ Corporation
Date: June 15, 2023
Location: Main Warehouse
,,,,,,
Item,Quantity,Price,Category,Supplier
Laptop,10,800,Electronics,A
Phone,20,500,Electronics,B
Printer,5,200,Electronics,C
,,,,,,
Item,Quantity,Price,Category,Supplier
Chair,20,50,Furniture,D
Desk,10,150,Furniture,E
Bookshelf,5,100,Furniture,F
```'''}]


def generate_sheet(chat, count):
    generated_chat = []

    for i in range(count):
        # Randomly select a spreadsheet type
        selected_type = random.choice(spreadsheet_types)
        selected_subtable_type = random.choice(subtable_type)
        selected_header = random.choice(header)
        prompt = {
            'role': 'user',
            'content': f'Generate an {selected_type} example {selected_subtable_type} {selected_header} formatted in csv code '}
        chat.append(prompt)

        # Generate a response using the conversation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat
        )

        # Get the assistant's reply
        assistant_reply = response.choices[0].message
        chat.append(assistant_reply)

        # Append the user and assistant messages to the generated_chat list
        generated_chat.append(
            {'user': prompt['content'], 'assistant': assistant_reply['content']})

        # Print the assistant's reply
        print(assistant_reply['content'])

    # Save the generated conversation to a JSON file
    with open('generated_conversation.json', 'w') as file:
        json.dump(generated_chat, file, indent=4)


generate_sheet(chat=conversation, count=5)
