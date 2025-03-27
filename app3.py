import ollama
import time
all_labels = []
all_responses = []
def load_labels(file_path):
    """Load labels from a file and format them as a list."""
    labels = []
    global all_labels,all_responses
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip().replace("_", " ")
            all_labels.append(line) # Getting all labels
            if line not in labels:  # Avoid duplicates
                labels.append(line)

    # print(f"Total labels: {len(labels)}")
    labels = "\n- " + "\n- ".join(labels)  # Format labels for display
    # print(all_labels)
    return labels

def chat_with_gemma(labels):
    global all_labels,all_responses
    """Reads sentences from seq.txt, processes them in batches, and prints responses immediately after each batch."""
    system_message = {
        "role": "system",
        "content": "You are an intent classification expert. Identify the intent of this sentence strictly from the predefined list. Do not generate any new intents. Respond only with the intent name. List : "
    }

    sentences = []
    with open("seq.txt", "r", encoding="utf-8") as file:
        for line in file:
            sentences.append(line.strip())  # Read each line and store in list

    batch_size = 20  # Process 20 sentences at a time

    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]  # Take a batch of sentences
        user_messages = [{"role": "user", "content": f"{labels}. Sentence: {sentence}"} for sentence in batch]
        start_time = time.time()
        # Call Ollama API for each sentence in the batch
        batch_responses = [ollama.chat(model="gemma2", messages=[system_message, msg]) for msg in user_messages]
        end_time = time.time()
        # Print results for the current batch immediately
        print(f"\n--- Batch {i // batch_size + 1} ---\n")
        print(f"time taken for batch {i+1} : ",end_time - start_time)
        for sentence, response in zip(batch, batch_responses):
            print("Sentence:", sentence)
            print("Gemma:", response['message']['content'])
            print("-" * 50)
            all_responses.append(response['message']['content'].strip()) # Store all responses
            # print(all_responses)

    c=0
    for i in range(0,len(all_responses),1):
        if all_responses[i] == all_labels[i]:
            c=c+1
    print(c)


if __name__ == "__main__":
    labels = load_labels("label.txt")  # Load labels
    # print(labels, "\n")  # Print labels
    chat_with_gemma(labels)  # Start chat