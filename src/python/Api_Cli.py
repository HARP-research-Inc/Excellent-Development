# Usage: 
# <user puts spreadsheets in question in designated folder>
# Terminal: Please place requested files in the Input folder. Begin Analysis? Y/N
# User: Y
# Terminal: Analyzing...
# Terminal: Analysis complete.
# Terminal: Please provide a query, or type EXIT to exit: 
# User: What is the area of Finland?
# Terminal: 4500 square miles.
# Terminal: Query:
# User: What is my favorite color?
# Terminal: Sorry, I don't know that information.
# Terminal: Query:
# User: EXIT
# Terminal: Goodbye!

import os
from time import sleep

def analyze_files(directory):
    filelist = os.listdir(directory)
    filecount = len(filelist)
    progress = 0
    print("Analyzing...")
    for i, filename in enumerate(filelist):
        if filename.endswith(".xlsx") or filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            print(f"Analyzing file: {file_path}")
            analyze_file(file_path)
            progress += 1
            print_progress(progress, filecount)
    print("Analysis complete.")

def analyze_file(file_path):
    # analyze the file here
    # Harper bit
    # add to vector db here - Kevin
    sleep(1)

def print_progress(progress, total):
    percent = (progress / total) * 100
    print(f"Progress: {progress}/{total} ({percent:.2f}%)", end="\r")
    if progress == total:
        print()

def handle_query(query):
    # Handle query here
    # Hacky api bit
    if query.lower() == "what is the area of finland?":
        return "4500 square miles."
    elif query.lower() == "what is my favorite color?":
        return "Sorry, I don't know that information."
    else:
        return "I don't understand that query."

def main():
    print("Please place requested files in the Input folder. Begin Analysis? Y/N")
    user_input = input()
    if user_input.lower() == 'y':
        directory = user_input.lower()
        analyze_files(directory)
        while True:
            print("Please provide a query, or type EXIT to exit:")
            query = input()
            if query.lower() == "exit":
                print("Goodbye!")
                break
            else:
                response = handle_query(query)
                print(response)
    else:
        print("Goodbye!")

if __name__ == "__main__":
    while True:
        main()
