from flask import Flask, render_template, request, jsonify
import ollama

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
    user_message = f"""
    Analyze the following user message and classify its intent concisely.

    User Message: "{user_message}"

    Provide only the intent as a one- or two-word label, without any explanations. 
    Then, compute similarity scores between the generated intent and the following predefined intents: 
    {user_words}.

    Formst the output as follows:
    Intent: <generated_intent> 
    Similarity Scores: 
    <intent 1>: <score 1>
    <intent 2>: <score 2>
    <intent 3>: <score 3> 
    and so on.
    """
    response = ollama.chat(model='gemma2', messages=[{'role': 'user', 'content': user_message}])
    bot_reply = response.get('message', {}).get('content', 'Error generating response')
    return jsonify({'reply': f"{bot_reply}"})

if __name__ == '__main__':
    app.run(debug=True)
