import time
from sheet_chunker_manual import output_func
from sheet_chunker_optimized import test_func
from sheet_chunker_reoptimized import test_func as retest_func
import os
import sys

# Custom NullWriter class to suppress output
class NullWriter:
    def write(self, s):
        pass

# Function to measure execution time
def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Start the timer
        
        # Suppress terminal output by redirecting stdout to NullWriter
        old_stdout = sys.stdout
        sys.stdout = NullWriter()

        result = func(*args, **kwargs)  # Call the function

        sys.stdout = old_stdout

        end_time = time.time()  # Stop the timer
        execution_time = end_time - start_time  # Calculate the execution time
        print(f"Execution time: {execution_time:.6f} seconds")
        return result
    return wrapper

# Example functions to measure execution time
@measure_execution_time
def measure_output_func():
    print("testing original:")
    output_func()

@measure_execution_time
def measure_optimized_func():
    print("testing optimized:")
    test_func()

@measure_execution_time
def measure_reoptimized_func():
    print("testing reoptimized:")
    retest_func()

# Call the functions with execution time measurement
measure_output_func()
measure_optimized_func()
measure_reoptimized_func()
