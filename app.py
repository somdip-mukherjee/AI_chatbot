import ollama
import re
import time
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report
import csv
import os

# qwen2.5:32b
# deepseek-r1:32b
# phi4
# phi 3
# llama3.1

    # models used :
    # ollama run phi4 14b 
    # ollama run llama3.1 8b
    # ollama run mistral 8b
    # ollama run qwen2.5 7b
    # ollama run gemma2 9b
    # ollama run phi3  3.8b
    # ollama run falcon 7b
    # ollama run gemma3:4b
    # ollama run gemma3:12b
    # ollama run gemma3:27b
    # ollama run gemma3:1b   rohan
    # ollama run deepseek-r1:1.5b
    # ollama run deepseek-r1:8b
    # ollama run deepseek-r1:14b
    # ollama run gemma2:27b
    # ollama run phi3:14b
    # ollama run deepseek-r1:32b
    # ollama run qwen2.5:32b
    # mistral-nemo 12b



all_labels = []
all_responses = []

seq_dataset_name = "clinc_seq_15000.txt"   #rohan
labels_dataset_name = "clinc_label_15000.txt"   #rohan

models = [ "gemma2" ,"gemma2:27b" , "gemma3:1b" , "gemma3:12b" , "gemma3:27b" , "llama3.1" , "phi3:14b" , "phi4" , "qwen2.5:32b" , "qwen2.5" , "mistral" ,  "mistral-nemo" , "deepseek-r1:1.5b" , "deepseek-r1:8b" ]

# models = [ "gemma3:1b" ] 

# models = [ "deepseek-r1:32b ]   will be used later

def load_labels(file_path):
    """Load labels from a file and format them as a list."""
    labels = []
    global all_labels,all_responses
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip().replace("_"," ")
            line = line.lower()
            line = line.replace("-"," ")
            all_labels.append(line) # Getting all labels
            if line not in labels:  # Avoid duplicates
                labels.append(line)
    # print("all labels : ",all_labels)
    return labels


def chat_with_gemma(labels):
    global all_labels,all_responses , labels_seq_dataset_name , seq_dataset_name
    """Reads sentences from dataset, processes them in batches, and prints responses immediately after each batch."""
    system_message = {
        "role": "system",
        "content": f"You are an intent classification expert. Identify the intent of this sentence strictly from the predefined list. Respond with only the intent name. No additional text, no explanations, no greetings , no reasoning. List of intents: {', '.join(labels)}. "
    }
    sentences = []
    with open(seq_dataset_name, "r", encoding="utf-8") as file:
        for line in file:
            sentences.append(line.strip())  # Read each line and store in list

    for model in models : 
        all_responses = []
        i=0
        total_time = 0 

        ollama.chat(model=model, messages=[system_message,{"role": "user", "content": f"Sentence: why isn't my google pay top up working?"}]) # loads models removes outlier , dummy prompt

        for sentence in sentences : 
            i=i+1
            user_message = {"role": "user", "content": f"Sentence: {sentence}"}
            start_time = time.time()
            # Call Ollama API for each sentence
            response = ollama.chat(model=model, messages=[system_message, user_message])
            end_time = time.time()
            # Print results
            time_taken = round(end_time - start_time,2)
            total_time=total_time+time_taken
            print(f"time taken for sentence  {i} : {time_taken} seconds")
            print("Sentence: ", sentence)
            print(f"{model}: ", response['message']['content'])
            print("-" * 50)
            resp = response['message']['content'] 
            if "_" in resp :
                resp = resp.replace("_"," ")
            if "-" in resp :
                resp = resp.replace("-"," ")
            if '\\' in resp :
                resp = resp.replace('\\','')
            all_responses.append(resp.strip().lower()) # Store all responses

        # report calculations 
        if len(all_labels) == len(all_responses):
            c=0
            for j in range(0,len(all_responses),1):
                if all_labels[j] in all_responses[j]:
                    all_responses[j] = all_labels[j]
                    c=c+1
            print(c)
            dataset_size = len(all_labels)
            accuracy =( c / dataset_size ) * 100
            avg_latency = total_time/dataset_size
        else :
            print("length not match")

        # print(f"sentences : {all_labels} , all responses : {all_responses}")
        y_true = all_labels # ground truth
        y_pred = all_responses # model predictions

        # Calculate Precision, Recall, and F1-Score
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

        # s = f"Accuracy for model name = {model} , dataset size : {dataset_size} sentences , accuracy = {accuracy:.4f} % , average latency : {avg_latency:.4f} seconds , Precision: {precision:.4f} , Recall: {recall:.4f} ,  F1-Score: {f1:.4f} "

        # with open("classification_report.txt","a") as file :
        #     file.write(s+"\n")

                
        csv_file = "classification_report.csv"    # rohan 

        # Check if the file exists to write headers only once
        file_exists = os.path.isfile(csv_file)

        # Open CSV file in append mode
        with open(csv_file, "a", newline="") as file:
            writer = csv.writer(file)

            # Write header only if file is newly created
            if not file_exists:
                writer.writerow(["Model Name","Dataset Name", "Dataset Size (number of sentences)", "Accuracy (%)", "Avg Latency (s)", "Precision", "Recall", "F1-Score"])

            # Write data row

            writer.writerow([model,f"{seq_dataset_name}", dataset_size, f"{accuracy:.4f}", f"{avg_latency:.4f}", f"{precision:.4f}", f"{recall:.4f}", f"{f1:.4f}"])

if __name__ == "__main__":
    # global seq_dataset_name , labels_seq_dataset_name
    labels = load_labels(labels_dataset_name)  # Load labels
    chat_with_gemma(labels)  # Start chat