# import openpyxl
# import json
# from openpyxl import load_workbook

# def clean_data(value):
#     if value is None or value == '-':
#         return '0'
#     return str(value).replace(',', '').replace('(', '').replace(')', '')

# def get_sheet_dict(ws):
#     sheet_dict = {}
#     data_dict = {}
#     item_name = None
#     months = [cell.value for cell in ws[2]]  # Month names assumed to be in the second row

#     for row in ws.iter_rows(min_row=3, values_only=True):  # Data assumed to start from third row
#         current_item = row[0]
#         # If the first column has a value, it indicates a new item begins
#         if current_item is not None:
#             # If there is an existing item, add it to the sheet dictionary before moving on
#             if item_name is not None:
#                 sheet_dict[item_name] = data_dict
#             # Initialize new data dictionary
#             data_dict = {}
#             item_name = current_item
#         # Add the row of data under the current item
#         data = [clean_data(cell) for cell in row[1:]]
#         data_dict = dict(zip(months, data))

#     # Add the last item to the sheet dictionary
#     if item_name is not None:
#         sheet_dict[item_name] = data_dict

#     return sheet_dict

# # MAIN
# if __name__ == '__main__':

#     wb = load_workbook(
#         filename="E:\GDrive\Harpers Startup\Excellent-Development\src\python\single_test.xlsx",
#         read_only=False,
#         data_only=True)

#     budget_dict = {}

#     for ws in wb:
#         year_dict = get_sheet_dict(ws)
#         budget_dict[ws.title] = year_dict

#     data_json = json.dumps(budget_dict, indent=4)  # pretty print JSON

#     with open("new.json", "w") as f:
#         f.write(data_json)

#     print(data_json)

import pandas as pd

def excel_to_json(excel_file, json_file):
    # Load spreadsheet
    xl = pd.ExcelFile(excel_file)

    # Load a sheet into a DataFrame by its name
    df = xl.parse(xl.sheet_names[0])

    # Fill in the NULL values for "-"
    df = df.fillna("NULL")

    # Convert the DataFrame to JSON
    json_data = df.to_json(orient="index")

    # Write the JSON data to file
    with open(json_file, "w") as json_file:
        json_file.write(json_data)

# Usage
excel_to_json("E:\GDrive\Harpers Startup\Excellent-Development\src\python\single_test.xlsx", "new.json")


import os
from langchain import HuggingFacePipeline
from transformers import AutoTokenizer, pipeline, LlamaForCausalLM, AutoModelForCausalLM
import torch
from langchain import PromptTemplate,  LLMChain
import requests
from torch.nn import DataParallel

model_path = "here_we_go_again/text-generation-webui/models/psmathur_wizardlm_alpaca_dolly_orca_open_llama_13b" #tiiuae/falcon-40b-instruct
model = DataParallel(AutoModelForCausalLM.from_pretrained(model_path, device_map='auto'))
tokenizer = AutoTokenizer.from_pretrained(model_path) 
device = torch.device("cuda")
model.to(device)

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:16" 
pipeline = pipeline(
    "text-generation", #task
    model=model,
    tokenizer=tokenizer,
    # device= -1,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto",
    max_length=100,
    do_sample=True,
    top_k=10,
    num_return_sequences=1,
    eos_token_id=tokenizer.eos_token_id,
    
)

llm = HuggingFacePipeline(pipeline = pipeline, model_kwargs = {'temperature':0})

template = """
You are an intelligent chatbot. Help the following question with brilliant answers.
Question: {question}
Answer:"""
prompt = PromptTemplate(template=template, input_variables=["question"])

llm_chain = LLMChain(prompt=prompt, llm=llm)

question = "Explain what is Artificial Intelligence as Nursery Rhymes"

print(llm_chain.run(question))

