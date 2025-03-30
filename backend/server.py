import os
import json
import subprocess
import re
from typing import Dict, Any, List, Optional, Union
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import sys
import ast
from llama_stack_client import LlamaStackClient
from llama_stack_client.types import UserMessage

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# LlamaStack API configuration
LLAMA_HOST = "localhost"
LLAMA_PORT = 5001
LLAMA_MODEL = "meta-llama/Llama-3.2-3B-Instruct"

# Initialize LlamaStack client
llama_client = LlamaStackClient(
    base_url=f"http://{LLAMA_HOST}:{LLAMA_PORT}",
)

def call_llm_for_code(user_query: str) -> str:
    """Call the LLM to generate macOS API code for the given query"""
    
    system_prompt = """You are an AI that translates natural language commands into macOS system API calls using Python.
Generate ONLY valid Python code that can be executed to perform the requested action on macOS.
Your code should use the most appropriate low-level macOS APIs or commands.
For UI actions, prefer to use:
1. PyObjC and AppKit for direct macOS API access
2. AppleScript through subprocess.run for UI automation
3. Shell commands through subprocess for system tasks

Return ONLY the Python code with no explanation, commentary, or markdown. Just the raw Python code.
The code should be complete and executable as-is. Include all necessary imports at the top.
"""
    
    user_message = f"""Generate macOS API code for this command: "{user_query}"

Your code should be as flexible as possible and handle potential errors gracefully.
Here are some examples of the APIs you can use:
- NSWorkspace for app management
- NSRunningApplication for app control
- AppKit for UI elements
- CoreGraphics for screen and window management
- AppleScript for UI automation
- subprocess for system commands

The code will be executed directly, so make it safe and effective.
"""
    
    try:
        response = llama_client.inference.chat_completion(
            messages=[
                {
                    "content": system_prompt,
                    "role": "system"
                },
                {
                    "content": user_message,
                    "role": "user"
                }
            ],
            model_id=LLAMA_MODEL,
            stream=False,
        )
        
        return response.completion_message.content
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return "# Error generating code"

def is_code_safe(code: str) -> bool:
    """Basic safety check for the generated code"""
    # List of dangerous functions/modules we want to block
    dangerous_patterns = [
        # r"os\.rmdir", r"os\.unlink", r"os\.remove", r"shutil\.rmtree",
        # r"__import__\(['\"]os['\"]", r"globals\(\)", r"locals\(\)",
        # r"subprocess\.call\(['\"]rm", r"exec\(", r"eval\(",
    ]
    
    # Check for dangerous patterns
    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            return False
    
    # Try to parse the code to detect syntax errors
    try:
        ast.parse(code)
    except SyntaxError:
        return False
    
    return True
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
    
    # # First check if the code is safe
    # if not is_code_safe(code):
    #     return {"success": False, "message": "Generated code contains potentially unsafe operations", "output": ""}
    
    # Create a temporary file to hold the code
     # Clean the code before processing
    code = clean_generated_code(code)
    
    print("Code to be executed:")
    print("-------------------")
    print(code)
    print("-------------------")
    code_file = "temp_code.py"
    with open(code_file, "w") as f:
        f.write(code)
    
    # Execute the code in a separate process and capture output
    try:
        result = subprocess.run(
            ["python3", code_file],
            capture_output=True,
            text=True,
            timeout=60  # Set a timeout to prevent hanging
        )
        print("running python3 now")
        
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

# API Endpoints
@app.route('/process', methods=['POST'])
def process_command():
    """Process a natural language command by generating and executing code"""
    data = request.json
    if not data or 'command' not in data:
        return jsonify({"error": "No command provided"}), 400
    
    user_command = data['command']
    
    # 1. Generate code using LLM
    generated_code = call_llm_for_code(user_command)
    
    # 2. Execute the generated code
    result = execute_code(generated_code)
    
    # 3. Return the full response
    response = {
        "command": user_command,
        "generated_code": generated_code,
        "execution_result": result
    }
    
    return jsonify(response)

@app.route('/status', methods=['GET'])
def status():
    """Check if the backend service is running and connected to LlamaStack"""
    try:
        # Try a simple query to check if LlamaStack is responding
        test_response = llama_client.inference.chat_completion(
            messages=[
                UserMessage(
                    content="Test connection",
                    role="user",
                ),
            ],
            model_id=LLAMA_MODEL,
            max_tokens=10,
            stream=False,
        )
        
        if test_response:
            return jsonify({
                "status": "online", 
                "model": LLAMA_MODEL,
                "llama_stack": "connected"
            })
    except Exception as e:
        return jsonify({
            "status": "online", 
            "model": LLAMA_MODEL,
            "llama_stack": "disconnected",
            "error": str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5066)