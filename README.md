# AI Intent Classifier

This project is an AI-powered intent classification system using Flask, NiceGUI, and LangChain with Ollama LLM.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.8+
- Pip (Python package manager)
- Ollama installed (for running the `gemma2` model)
- A working internet connection (for package installations)

## Installation

Follow these steps to set up the environment:

### 1. Clone the Repository

```sh
git clone <repository_url>
cd <repository_name>

### 2. Install Required Dependencies

Run the following command to install all required Python packages:

pip install flask nicegui requests langchain_ollama langchain_core

### 3. Start Ollama and Load the Model

Ensure that Ollama is installed and running. If not, install it from Ollama's official website and then run:

ollama pull gemma2

### 4. Run the Application

Execute the script to start both the Flask backend and the NiceGUI frontend:

python <script_name>.py

Replace <script_name>.py with the actual filename.

### 5. Access the Application

The Flask backend will run at: http://localhost:5000

The NiceGUI frontend will be available at: http://localhost:8080

### How It Works

1. The NiceGUI frontend provides a user interface to send messages.


2. The Flask backend processes the input and uses Ollama's gemma2 model to classify the intent.


3. The classified intent is displayed in the UI.

