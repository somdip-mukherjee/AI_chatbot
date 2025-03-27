from flask import Flask, render_template, request, jsonify
import ollama
import json
import re

app = Flask(__name__)

# Store user words
data_store = {"words": []}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_words', methods=['POST'])
def update_words():
    words = request.json.get('words', [])
    if isinstance(words, list):
        data_store["words"] = [word.strip() for word in words if isinstance(word, str)]
    return jsonify({'message': 'Intents updated successfully', 'stored_words': data_store["words"]})

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    user_words = ', '.join(data_store["words"])

    prompt = f"""
    Analyze the following user message and classify its intent concisely.

    User Message: "{user_message}"

    Provide only the intent as a one- or two-word label, without any explanations. 
    Then, compute similarity scores between the generated intent and the following predefined intents: 
    {user_words}.

    Format the output in JSON with the structure:
    {{
        "<intent 1>": <score 1>,
        "<intent 2>": <score 2>,
        "<intent 3>": <score 3>
    }}
    """

    response = ollama.chat(model='gemma2', messages=[{'role': 'user', 'content': prompt}])
    bot_reply = response.get('message', {}).get('content', '')

    # Extract JSON response from model output
    match = re.search(r'{.*}', bot_reply, re.DOTALL)
    if match:
        try:
            parsed_json = json.loads(match.group())  # Convert extracted string to JSON object
            json_string = json.dumps(parsed_json, indent=4)  # Convert JSON object to a formatted JSON string
        except json.JSONDecodeError:
            json_string = json.dumps({"error": "Failed to parse JSON"})
    else:
        json_string = json.dumps({"error": "Invalid response format"})

    return jsonify({"reply": json_string})  # Return JSON string inside JSON object

if __name__ == '__main__':
    app.run(debug=True)