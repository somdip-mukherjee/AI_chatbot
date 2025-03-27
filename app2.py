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
            all_labels.append(line)  # Storing all labels
            if line not in labels:  # Avoid duplicates
                labels.append(line)

    return "\n- " + "\n- ".join(labels)  # Format labels for display

def chat_with_gemma(labels):
    global all_labels, all_responses
    """Reads sentences from seq.txt, processes them in batches, and prints responses immediately after each batch."""
    
    system_message = {
        "role": "system",
        "content": ("You are an intent classification expert. Identify the intent of each sentence strictly from the predefined list. "
                    "Do not generate new intents. Respond only with the intent name for each sentence in the same order.\n\nList:")
    }

    sentences = []
    with open("seq.txt", "r", encoding="utf-8") as file:
        for line in file:
            sentences.append(line.strip())  # Read each line and store in list

    batch_size = 20  # Process 20 sentences at a time

    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]  # Take a batch of sentences

        # Format the batch as a single user message
        batch_text = "\n".join([f"{j+1}. {sentence}" for j, sentence in enumerate(batch)])
        user_message = {
            "role": "user",
            "content": f"{labels}\n\nHere are multiple sentences:\n{batch_text}\n\nProvide only the intent name for each sentence in the same order, one per line."
        }

        start_time = time.time()

        # Send a single request for the whole batch
        response = ollama.chat(model="gemma2", messages=[system_message, user_message])
        
        end_time = time.time()

        # Extract intents from the response
        response_text = response['message']['content'].strip().split("\n")  # Split responses into a list
        batch_responses = [intent.strip() for intent in response_text if intent.strip()]  # Remove empty lines

        # Ensure batch_responses count matches batch count (handles any formatting issues)
        if len(batch_responses) != len(batch):
            print(f"Warning: Response count mismatch. Expected {len(batch)}, got {len(batch_responses)}.")
            continue  # Skip this batch if there's an issue

        # Print results for the current batch
        print(f"\n--- Batch {i // batch_size + 1} ---\n")
        print(f"Time taken for batch {i // batch_size + 1}: {end_time - start_time:.2f} seconds")

        for sentence, intent in zip(batch, batch_responses):
            print("Sentence:", sentence)
            print("Gemma:", intent)
            print("-" * 50)
            all_responses.append(intent)  # Store all responses

    # Accuracy check
    correct_count = sum(1 for i in range(len(all_responses)) if i < len(all_labels) and all_responses[i] == all_labels[i])
    print(f"\nCorrect Predictions: {correct_count}/{len(all_responses)} ({(correct_count / len(all_responses) * 100):.2f}%)")

if __name__ == "__main__":
    labels = load_labels("label.txt")  # Load labels
    chat_with_gemma(labels)  # Start chat