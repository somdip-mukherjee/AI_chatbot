import subprocess

# List of models to download
models = [
    "llama2:13b",
    "mistral",
    "vicuna:13b-q4_K_M",
    "stable-beluga:13b-q4_K_M",
    "orca-mini:13b-q4_K_M",
]



# Function to download models
def download_models():
    for model in models:
        print(f"Downloading {model}...")
        try:
            # Run the Ollama pull command
            subprocess.run(["ollama", "pull", model], check=True)
            print(f"✅ Successfully downloaded {model}\n")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to download {model}\n")

if __name__ == "__main__":
    download_models()
    print("🎉 All models downloaded!")