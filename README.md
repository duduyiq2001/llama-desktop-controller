# MacOS LLM Controller

MacOS LLM Controller is a desktop application that allows users to execute macOS system commands using natural language input. It leverages a React-based frontend and a Flask-based backend integrated with LlamaStack to generate and execute Python code for macOS API calls.

## Features
- Execute macOS system commands via natural language.
- Supports text and voice input for commands.
- Displays command execution history with real-time status updates.
- Backend integration with LlamaStack for Python code generation.

[Link to Demo](https://www.loom.com/share/6b3f665f14164daa8d3e45a8b6ac61f0?sid=b6078c87-e26a-4321-b645-b3ec8064a9c7)
---

## Technical Architecture

### Frontend
- **Framework**: React with Vite for fast development and bundling.
- **Key Features**:
  - Command input via text or voice (using the SpeechRecognition API).
  - Real-time service status indicator.
  - Command execution history with success/error feedback.
- **Proxy Configuration**: API requests are proxied to the Flask backend.

### Backend
- **Framework**: Flask with Flask-CORS for handling API requests.
- **Key Features**:
  - Integrates with LlamaStack to generate Python code for macOS commands.
  - Executes the generated Python code and returns the results.
  - Provides a `/status` endpoint to check service and LlamaStack connectivity.
- **Dependencies**: Flask, Flask-CORS, requests, pyobjc, llama-stack-client.

### LlamaStack Integration
- **Model**: Llama-3.2-3B-Instruct.
- **Purpose**: Translates natural language commands into Python code for macOS API calls.
- **Safety**: Basic checks are performed to ensure the generated code is safe and executable.

---

## Installation and Setup

### Prerequisites
1. **Node.js** (v16 or later) and **npm**.
2. **Python** (v3.8 or later) with `pip` installed.
3. **LlamaStack** running on `http://localhost:5001`.

---

### Steps to Run

# LLaMA Stack Setup

## Environment Variables
Set the inference model names:
```sh
export INFERENCE_MODEL="meta-llama/Llama-3.2-3B-Instruct"

# Ollama names this model differently, and we must use the Ollama name when loading the model
export OLLAMA_INFERENCE_MODEL="llama3.2:3b-instruct-fp16"
```

## Running the Model with Ollama
Start the Ollama inference server with a 60-minute keepalive:
```sh
ollama run $OLLAMA_INFERENCE_MODEL --keepalive 60m
```

## Running LLaMA Stack with Docker
Set the port and run the container:
```sh
export LLAMA_STACK_PORT=5001
docker run \
  -it \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  -v ~/.llama:/root/.llama \
  llamastack/distribution-ollama \
  --port $LLAMA_STACK_PORT \
  --env INFERENCE_MODEL=$INFERENCE_MODEL \
  --env OLLAMA_URL=http://host.docker.internal:11434
```

#### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd /Users/sahil/Downloads/Llama-Stack Demo Apps/desktop_controller/llama-desktop-controller/backend
2. Install Python dependencies:
     ```sh
     pip install -r ../requirements.txt
     ```
3. Start the Flask server:
   ```sh 
   python server.py
   ```
4. The backend will run on http://localhost:5066.

#### 2. Frontend Setup
1. Navigate to the frontend directory
  ```sh
  cd /Users/sahil/Downloads/Llama-Stack Demo Apps/desktop_controller/llama-desktop-controller
  ```
2. Install Node.js dependencies
  ```sh
  npm install
  ```
3. Start the development server
  ```sh
  npm run dev
  ```
4. The frontend will run on http://localhost:5173

#### 3. Access the Application
Open your browser and navigate to http://localhost:5173.
Ensure the backend and LlamaStack are running for full functionality.
