import openai
import re
import os

def parse_prompt(variables, input_structure, examples):
    # Initialize a list to store each completed example
    example_list = []

    # Iterate through each provided example
    for example in examples:
        # Prepare a copy of the input_structure for modification
        in_string = input_structure
        # Replace variables in in_string with formatted values for this example
        for variable, value in example["user"].items():
            in_string = in_string.replace(f'{{{variable}}}', f"<{variable}>{value}</{variable}>")

        # Initialize a string to store the assistant's responses
        out_string = ''
        # Format assistant's responses and append them to out_string
        for variable, value in example["assistant"].items():
            out_string += f"<{variable}>{value}</{variable}>\n"

        # Add the completed example (with formatted user input and assistant responses) to the list
        example_list.append(f"{in_string}\n\n{out_string.strip()}")

    # Prepare a copy of the input_structure for the final prompt
    prompt = input_structure
    # Replace variables in prompt with formatted values for the final prompt
    for variable, value in variables["in"].items():
        prompt = prompt.replace(f'{{{variable}}}', f"<{variable}>{value}</{variable}>")

    # Add the actual prompt to the list
    example_list.append(prompt)

    # Return all examples and the prompt, separated by two newlines
    return '\n\n'.join(example_list)

def prompt_interface(openai_api_key, variables, input_structure, examples, system_message=None):
    # Configure OpenAI API key
    openai.api_key = openai_api_key
    
    # Prepare prompt by inserting variable values and examples into system message
    prompt = parse_prompt(variables, input_structure, examples)

    # Extract tag names from variable keys
    tag_names = variables["out"]

    # Define retry count
    retry_count = 3

    while retry_count > 0:
        try:
            # Generate a response using the conversation
            completions = openai.Completion.create(
                model="text-davinci-003",
                temperature=0.5,         
                prompt=prompt,
                max_tokens=100,
                n=1,
            )

            # Get the assistant's reply
            assistant_reply = completions.choices[0].text.strip()

            # Check output for correct format and extract data
            response_dict = {}
            for tag in tag_names:
                pattern = f"<{tag}>(.*?)</{tag}>"
                match = re.search(pattern, assistant_reply)
                if match is None:
                    raise ValueError(f"Output is missing tag {tag}")
                response_dict[tag] = match.group(1)
            
            # If output is correctly formatted, return result
            return response_dict

        except ValueError as e:
            print(f"Error: {str(e)}")
            retry_count -= 1
            if retry_count == 0:
                print("Failed to generate correctly formatted output after 3 attempts")
                return None
            else:
                print(f"Retrying... {retry_count} attempts remaining")


# Usage
openai_api_key = os.getenv('openai_api_key')
variables = {"in":{"x": "5", "y": "3","z": "7"},"out":["result","operation"]}
input_structure = "Calculate the following: {x} + {y} - {z}"
examples = [
    {
        "user": {"x": "2", "y": "3", "z": "1"}, 
        "assistant": {"result": "4", "operation": "addition and subtraction"}
    },
    {
        "user": {"x": "10", "y": "5", "z": "2"}, 
        "assistant": {"result": "13", "operation": "addition and subtraction"}
    },
    {
        "user": {"x": "7", "y": "3", "z": "2"}, 
        "assistant": {"result": "8", "operation": "addition and subtraction"}
    },
]

print(prompt_interface(openai_api_key, variables, input_structure, examples))
