import openai
import re
import os

def prompt_interface(openai_api_key, variables: dict, tag_names, examples, prompt, system_message=None):
    # Configure OpenAI API key
    openai.api_key = openai_api_key

    # Prepare prompt by inserting variable values and examples into system message
    # Adjust the prompt preparation as per your requirement
    prompt = system_message.format(**variables, tag_names=tag_names, examples=examples) if system_message else examples
    #examples_str = "\n".join(f"{ex['user'].format(**variables)}\n\n{ex['assistant'].format(**variables)}\n" for ex in examples)

    print(prompt)

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
            assistant_reply = completions.choices[0].text
            print(assistant_reply)

            # Check output for correct format
            for tag in tag_names:
                if not re.search(f"<{tag}>.*</{tag}>", assistant_reply):
                    raise ValueError(f"Output is missing tag {tag}")
            
            # If output is correctly formatted, return result
            return assistant_reply

        except ValueError as e:
            print(f"Error: {str(e)}")
            retry_count -= 1
            if retry_count == 0:
                print("Failed to generate correctly formatted output after 3 attempts")
                return None
            else:
                print(f"Retrying... {retry_count} attempts remaining")

# Usage
variables = {"x": "5", "y": "3"}
tag_names = ["mathq", "mathout"]
examples = [
    {"user": "<mathq>Calculate the sum of {x} and {y}</mathq>", "assistant": "<mathout>8</mathout>"},
    {"user": "<mathq>Subtract {y} from {x}</mathq>", "assistant": "<mathout>2</mathout>"}
]

examples = "Subtract 5 from 65 \n 60 \n Subtract 27 from 29 \n 2 \n"
openai_api_key = os.getenv('openai_api_key')
result = prompt_interface(openai_api_key, variables, tag_names, examples)
print(result)
