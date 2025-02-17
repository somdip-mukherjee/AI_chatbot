from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from nicegui import ui
import requests
import threading
import difflib
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from sentence_transformers import SentenceTransformer, util

# Initialize Flask app with SocketIO
app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")

# Predefined list of intents
ALL_INTENTS = ["greeting", "question", "complaint", "request", "farewell", "feedback"]

# Selected intents (User can modify this)
selected_intents = ["question", "request", "feedback"]
custom_intents = []  # Store user-defined intents

# Initialize SBERT model for semantic similarity
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

# Define chatbot logic
template = """
Analyze the user's message and classify its intent concisely.

Here is the conversation history: {history}

User Message: {question}

Classify the intent from this list only: {allowed_intents}

Provide only the intent in one or two words, without explanations.

Intent:
"""

unrestricted_template = """
Analyze the user's message and classify its intent concisely.

Here is the conversation history: {history}

User Message: {question}

Provide only the intent in one or two words, without explanations.

Intent:
"""

model = OllamaLLM(model="gemma2")
prompt = ChatPromptTemplate.from_template(template)
unrestricted_prompt = ChatPromptTemplate.from_template(unrestricted_template)
chain = prompt | model
unrestricted_chain = unrestricted_prompt | model

history = ""

def calculate_similarity(intent1, intent2):
    """Compute cosine similarity between two intents."""
    vector1 = similarity_model.encode(intent1, convert_to_tensor=True)
    vector2 = similarity_model.encode(intent2, convert_to_tensor=True)
    score = util.pytorch_cos_sim(vector1, vector2).item()
    return round(score, 2)  # Round off for better readability

@app.route('/chat', methods=['POST'])
def chat():
    global history, selected_intents, custom_intents
    user_input = request.json.get("question", "")
    allowed_intents = selected_intents + custom_intents

    # Step 1: Classify intent using selected and custom intents
    result = chain.invoke({"history": history, "question": user_input, "allowed_intents": ", ".join(allowed_intents)})
    result = result.strip().lower()

    # Step 2: Classify intent without any restrictions
    unrestricted_result = unrestricted_chain.invoke({"history": history, "question": user_input})
    unrestricted_result = unrestricted_result.strip().lower()

    # Step 3: Calculate semantic similarity for all intents
    similarity_scores = {intent: calculate_similarity(intent, unrestricted_result) for intent in allowed_intents}
    
    response_text = "Intent Similarities:\n" + "\n".join([f"{intent}: {score}" for intent, score in similarity_scores.items()])
    history += f"\nUser: {user_input}\nBot: {response_text}"

    return jsonify({"response": response_text})

@app.route('/update_intents', methods=['POST'])
def update_intents():
    global custom_intents
    custom_intents = request.json.get("custom_intents", [])
    return jsonify({"message": "Custom intents updated successfully!"})

@ui.page('/')
def main():
    ui.label("AI Intent Classifier").classes("text-3xl font-bold text-center text-black mb-4")

    ui.label("Enter Custom Intents:")
    custom_intents_input = ui.textarea(placeholder="Write custom intents, separated by commas...").classes("w-full p-2 border rounded-lg")
    
    def send_update():
        new_intents = [intent.strip() for intent in custom_intents_input.value.split(',') if intent.strip()]
        requests.post("http://localhost:5000/update_intents", json={"custom_intents": new_intents})
        ui.notify("Custom intents updated!")
    
    ui.button("Update Intents", on_click=send_update).classes("bg-green-500 hover:bg-green-600 text-white font-semibold px-4 py-2 rounded-lg shadow mb-4")

    ui.label("Chat with the AI:")
    chat_container = ui.column().classes("w-full h-[400px] overflow-auto border border-gray-300 rounded-lg p-4 bg-white shadow")

    with ui.row().classes("w-full mt-4 gap-2"):
        user_input = ui.input(placeholder="Type your message...").classes("bg-white text-black border border-gray-400 rounded-lg px-4 py-2 w-full shadow")
        ui.button("Send", on_click=lambda: send_message(user_input, chat_container)).classes("bg-blue-500 hover:bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg shadow")

def send_message(user_input, chat_container):
    user_text = user_input.value.strip()
    user_input.value = ""

    if not user_text:
        return

    with chat_container:
        ui.chat_message(user_text, name="You").classes("bg-blue-500 text-white p-2 rounded-lg max-w-sm")

    try:
        response = requests.post("http://localhost:5000/chat", json={"question": user_text})
        response_text = response.json().get("response", "Error: No response")
    except:
        response_text = "Error: Backend not running"

    with chat_container:
        ui.chat_message(response_text, name="Bot").classes("bg-gray-300 text-black p-2 rounded-lg max-w-sm")        

# Run Flask in a separate thread with SocketIO
def run_flask():
    socketio.run(app, port=5000, allow_unsafe_werkzeug=True)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Run NiceGUI
ui.run(port=8080)
