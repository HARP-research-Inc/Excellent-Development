import pytest
import openai
import os
from unittest.mock import Mock, patch
from src.open_ai_demo_python.prompt_interface import parse_prompt, prompt_interface

def test_parse_prompt_single_example():
    variables = {"in":{"x": "5", "y": "3"},"out":["result"]}
    input_structure = "{x} + {y}"
    examples = [
        {"user": {"x": "2", "y": "3"}, "assistant": {"result": "5"}},
    ]
    result = parse_prompt(variables, input_structure, examples)
    expected_result = "<x>2</x> + <y>3</y>\n\n<result>5</result>\n\n<x>5</x> + <y>3</y>"
    assert result == expected_result


def test_parse_prompt_multiple_examples():
    variables = {"in":{"x": "5", "y": "3"},"out":["result"]}
    input_structure = "{x} + {y}"
    examples = [
        {"user": {"x": "2", "y": "3"}, "assistant": {"result": "5"}},
        {"user": {"x": "3", "y": "3"}, "assistant": {"result": "6"}},
    ]
    result = parse_prompt(variables, input_structure, examples)
    expected_result = "<x>2</x> + <y>3</y>\n\n<result>5</result>\n\n<x>3</x> + <y>3</y>\n\n<result>6</result>\n\n<x>5</x> + <y>3</y>"
    assert result == expected_result

def test_parse_prompt_no_variables():
    variables = {"in":{},"out":{}}
    input_structure = "Hello World!"
    examples = []
    result = parse_prompt(variables, input_structure, examples)
    expected_result = "Hello World!"
    assert result == expected_result

def test_prompt_interface_success():
    with patch('openai.Completion.create') as mock_create:
        # Create a mock OpenAI API response
        mock_create.return_value = Mock(choices=[Mock(text='<result>5</result>')])
        
        # Define input parameters
        openai_api_key = "dummy_key"
        variables = {"in": {"x": "5", "y": "3"}, "out": ["result"]}
        input_structure = "{x} + {y}"
        examples = [{"user": {"x": "2", "y": "3"}, "assistant": {"result": "5"}}]

        # Call the function
        result = prompt_interface(openai_api_key, variables, input_structure, examples)
        
        # Check the result
        assert result == {"result": "5"}

def test_prompt_interface_failure():
    with patch('openai.Completion.create') as mock_create:
        # Create a mock OpenAI API response with missing tag
        mock_create.return_value = Mock(choices=[Mock(text='<result></result>')])
        
        # Define input parameters
        openai_api_key = "dummy_key"
        variables = {"in": {"x": "5", "y": "3"}, "out": ["result"]}
        input_structure = "{x} + {y}"
        examples = [{"user": {"x": "2", "y": "3"}, "assistant": {"result": "5"}}]

        # Call the function
        result = prompt_interface(openai_api_key, variables, input_structure, examples)
        
        # Check the result - it should be None due to missing data for 'result' tag
        assert result["result"] == ''
