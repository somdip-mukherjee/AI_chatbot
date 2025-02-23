Chatbot with Intent Classification

This project is a Flask-based chatbot that classifies user messages into intents using the gemma2 model from ollama. It also allows users to store custom intents and receive similarity scores between their input and predefined intents.

Features

Accepts user-defined intents

Classifies messages based on predefined intents

Generates similarity scores for classification

Uses Flask for backend and ollama for AI-based processing


Requirements

Ensure you have the following installed before running the project:

Python 3.x

Flask

Ollama Python package


Install dependencies using:

pip install flask ollama

Running the Project

1. Clone the repository or copy the script.


2. Run the Flask application using:



python app.py

3. Open a web browser and go to http://127.0.0.1:5000/



API Endpoints

POST /update_words

Updates the stored intents.

Request Body (JSON):

{
  "words": ["greeting", "request", "complaint"]
}

Response:

{
  "message": "Intents updated successfully",
  "stored_words": ["greeting", "request", "complaint"]
}

POST /chat

Sends a message to the chatbot for classification.

Request Body (JSON):

{
  "message": "I want a refund"
}

Response:

{
  "reply": "Intent: Refund Request\nSimilarity Scores:\n- greeting: 0.0\n- complaint: 0.8\n- request: 0.9"
}

Notes

Ensure ollama is properly set up and running.

Modify the predefined intents in index.html or via API as needed.

