from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Define prompt template
template = """
Answer the question below.

Here is the conversation history: {history}

Question: {question}

Answer: 
"""

# Load Ollama LLM model (make sure the model is installed in Ollama)
model = OllamaLLM(model="gemma2")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Chatbot function
def handle_conversation():
    history = ""  # Initialize history
    print("Welcome to the AI Chatbot! Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        # Get response from model
        result = chain.invoke({"history": history, "question": user_input})

        # Print bot response
        print("Bot: ", result)

        # Update conversation history
        history += f"\nUser: {user_input}\nAI: {result}"

if __name__ == "__main__":
    handle_conversation()