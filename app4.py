import ollama
import time

all_labels = []
all_responses = []

def load_labels(file_path):
    """Load labels from a file and format them as a list."""
    labels = []
    global all_labels, all_responses
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip().replace("_", " ")
            all_labels.append(line)  # Getting all labels
            if line not in labels:  # Avoid duplicates
                labels.append(line)

    return "\n- " + "\n- ".join(labels)  # Format labels for display

def chat_with_gemma(labels, model_session):
    global all_labels, all_responses
    """Reads sentences from seq.txt and sends them one by one while keeping the model loaded."""

    system_message = {
        "role": "system",
        "content": ("You are an intent classification expert. Identify the intent of the given sentence strictly from the predefined list. Do not generate new intents. Respond only with the intent name.\n\nList:")
    }

    with open("seq.txt", "r", encoding="utf-8") as file:
        sentences = [line.strip() for line in file]  # Read all lines

    for i, sentence in enumerate(sentences):
        user_message = {
            "role": "user",
            "content": f"{labels}. Sentence: {sentence}"
        }

        start_time = time.time()

        # Send message one by one while keeping the model open
        response = model_session.chat(messages=[system_message, user_message])

        end_time = time.time()

        # Extract intent from the response
        intent = response['message']['content'].strip()

        # Print results immediately
        print(f"\n--- Sentence {i + 1} ---\n")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print("Sentence:", sentence)
        print("Gemma:", intent)
        print("-" * 50)

        all_responses.append(intent)  # Store response

    # Accuracy check
    correct_count = sum(1 for i in range(len(all_responses)) if i < len(all_labels) and all_responses[i] == all_labels[i])
    print(f"\nCorrect Predictions: {correct_count}/{len(all_responses)} ({(correct_count / len(all_responses) * 100):.2f}%)")

if __name__ == "__main__":
    labels = load_labels("label.txt")  # Load labels

    # **Persistent Ollama Model Session**
    model_session = ollama.Model("gemma2")  # Keeps the model loaded for efficiency

    chat_with_gemma(labels, model_session)  # Start chat