import ollama
import re
import time
import sys
from sklearn.metrics import precision_score, recall_score, f1_score
import csv
import os

# Global variables
all_labels = []
all_responses = []

# Set the model(s) you want to run
models = ["gemma3:1b"]  # You can add more models here if your system supports them

def load_labels(file_path):
    labels = []
    global all_labels
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip().replace("_", " ").lower().replace("-", " ")
            all_labels.append(line)
            if line not in labels:
                labels.append(line)
    return labels

def chat_with_model(labels, seq_dataset_name):
    global all_labels, all_responses

    sentences = []
    with open(seq_dataset_name, "r", encoding="utf-8") as file:
        for line in file:
            sentences.append(line.strip())

    for model in models:
        all_responses = []
        total_time = 0

        # Dummy call to warm up model
        system_message = {
            "role": "system",
            "content": f"You are an intent classification expert. Identify the intent of this sentence strictly from the predefined list. Respond with only the intent name. No extra text. List of intents: {', '.join(labels)}."
        }
        ollama.chat(model=model, messages=[system_message, {"role": "user", "content": "Sentence: test"}])

        for i, sentence in enumerate(sentences, 1):
            user_message = {"role": "user", "content": f"Sentence: {sentence}"}
            start_time = time.time()
            response = ollama.chat(model=model, messages=[system_message, user_message])
            end_time = time.time()

            time_taken = round(end_time - start_time, 2)
            total_time += time_taken

            resp = response['message']['content'].strip().lower()
            resp = re.sub(r"[_\\\-]", " ", resp)  # Clean up response
            all_responses.append(resp)

            print(f"time for sentence {i}: {time_taken}s")
            print(f"{model}: {resp}")
            print("-" * 50)

        # Evaluation
        if len(all_labels) == len(all_responses):
            c = 0
            for j in range(len(all_responses)):
                if all_labels[j] in all_responses[j]:
                    all_responses[j] = all_labels[j]
                    c += 1

            dataset_size = len(all_labels)
            accuracy = (c / dataset_size) * 100
            avg_latency = total_time / dataset_size

            y_true = all_labels
            y_pred = all_responses

            precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

            # Write to CSV
            csv_file = "classification_report.csv"
            file_exists = os.path.isfile(csv_file)
            with open(csv_file, "a", newline="") as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Model Name", "Dataset Name", "Dataset Size", "Accuracy (%)", "Avg Latency (s)", "Precision", "Recall", "F1-Score"])
                writer.writerow([model, os.path.basename(seq_dataset_name), dataset_size, f"{accuracy:.4f}", f"{avg_latency:.4f}", f"{precision:.4f}", f"{recall:.4f}", f"{f1:.4f}"])
        else:
            print("Mismatch in number of labels and responses.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python your_script.py <sequence_file_path> <labels_file_path>")
        sys.exit(1)

    seq_dataset_name = sys.argv[1]  #seq
    labels_dataset_name = sys.argv[2]   #

    labels = load_labels(labels_dataset_name)
    chat_with_model(labels, seq_dataset_name)
