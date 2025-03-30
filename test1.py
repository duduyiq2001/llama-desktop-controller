import os
import subprocess
import re
from typing import Dict, Any

def clean_generated_code(code: str) -> str:
    """Clean and format the generated code to ensure it's properly formatted"""
    # Remove any markdown code block markers that might have been included
    code = re.sub(r'^```python\s*', '', code)
    code = re.sub(r'\s*```$', '', code)
    code = re.sub(r'^```\s*', '', code)
    
    # Ensure proper indentation
    lines = code.split('\n')
    clean_lines = []
    for line in lines:
        clean_lines.append(line.rstrip())
    
    return '\n'.join(clean_lines)

def execute_code(code: str) -> Dict[str, Any]:
    """Execute the generated Python code and return the result"""
    
    # Clean the code before processing
    code = clean_generated_code(code)
    
    print("Code to be executed:")
    print("-------------------")
    print(code)
    print("-------------------")
    
    # Create a temporary file to hold the code
    code_file = "temp_code.py"
    with open(code_file, "w") as f:
        f.write(code)
    
    # Execute the code in a separate process and capture output
    try:
        print(f"Executing with: python3 {code_file}")
        result = subprocess.run(
            ["python3", code_file],
            capture_output=True,
            text=True,
            timeout=10  # Set a timeout to prevent hanging
        )
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        # Clean up the temporary file
        os.remove(code_file)
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": "Command executed successfully",
                "output": result.stdout
            }
        else:
            return {
                "success": False,
                "message": f"Error executing code (exit code {result.returncode})",
                "output": result.stderr
            }
    except subprocess.TimeoutExpired:
        # Clean up the temporary file
        if os.path.exists(code_file):
            os.remove(code_file)
        return {
            "success": False,
            "message": "Command execution timed out",
            "output": "Execution took too long and was terminated"
        }
    except Exception as e:
        # Clean up the temporary file
        if os.path.exists(code_file):
            os.remove(code_file)
        return {
            "success": False,
            "message": f"Exception during execution: {str(e)}",
            "output": str(e)
        }

# Test code to open Safari
safari_code = """
import subprocess

def open_safari():
    try:
        # Using subprocess to run Safari
        subprocess.run(['open', '-a', 'Safari'])
        return "Safari opened successfully"
    except FileNotFoundError:
        return "Error: Safari is not installed on this system."
    except Exception as e:
        return f"An error occurred: {e}"

# Run the function and print the result
result = open_safari()
print(result)
"""

# Try with markdown formatting to simulate LLM output
markdown_safari_code = """```python
import subprocess

def open_safari():
    try:
        # Using subprocess to run Safari
        subprocess.run(['open', '-a', 'Safari'])
        return "Safari opened successfully"
    except FileNotFoundError:
        return "Error: Safari is not installed on this system."
    except Exception as e:
        return f"An error occurred: {e}"

# Run the function and print the result
result = open_safari()
print(result)
```"""

print("\n=== Test 1: Regular Code ===")
result1 = execute_code(safari_code)
print("Result:", result1)

print("\n=== Test 2: Code with Markdown Formatting ===")
result2 = execute_code(markdown_safari_code)
print("Result:", result2)