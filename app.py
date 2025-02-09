from flask import Flask, request, jsonify
from nicegui import ui
import requests
import threading
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Flask App
app = Flask(__name__)

# Define chatbot logic
template = """
Analyze the user's message and classify its intent concisely.

Here is the conversation history: {history}

User Message: {question}

Provide only the intent in one or two words, without explanations.

Intent:
"""

model = OllamaLLM(model="gemma2")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

history = ""

@app.route('/chat', methods=['POST'])
def chat():
    global history
    user_input = request.json.get("question", "")

    result = chain.invoke({"history": history, "question": user_input})
    result = "The intent of the user is : " + result

    history += f"\nUser: {user_input}\nBot: {result}"

    return jsonify({"response": result})

@ui.page('/')
def main():
    # Page Styling (Lighter Theme)
    ui.label("AI Intent Classifier").classes("text-3xl font-bold text-center text-black mb-4")
    
    # Chat Container
    chat_container = ui.column().classes("w-full h-[400px] overflow-auto border border-gray-300 rounded-lg p-4 bg-white shadow")

    # Input & Button Container
    with ui.row().classes("w-full mt-4 gap-2"):
        user_input = ui.input(placeholder="Type your message...").classes("bg-white text-black border border-gray-400 rounded-lg px-4 py-2 w-full shadow")
        ui.button("Send", on_click=lambda: send_message(user_input, chat_container)).classes("bg-blue-500 hover:bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg shadow")

def send_message(user_input, chat_container):
    user_text = user_input.value.strip()
    user_input.value = ""

    if not user_text:
        return

    # User Message (No avatar to avoid errors)
    with chat_container:
        ui.chat_message(user_text, name="You").classes("bg-blue-500 text-white p-2 rounded-lg max-w-sm")

    try:
        response = requests.post("http://localhost:5000/chat", json={"question": user_text})
        response_text = response.json().get("response", "Error: No response")
    except:
        response_text = "Error: Backend not running"

    # Bot Message (No avatar to avoid errors)
    with chat_container:
        ui.chat_message(response_text, name="Bot").classes("bg-gray-300 text-black p-2 rounded-lg max-w-sm")        
# Run Flask in a separate thread
def run_flask():
    app.run(port=5000, use_reloader=False)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Run NiceGUI
ui.run(port=8080)