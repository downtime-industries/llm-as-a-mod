#!/usr/bin/env python3
import os
import subprocess
import sys


MODEL_BASE_DIR = os.path.join(os.getcwd(), "models")
os.makedirs(MODEL_BASE_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_BASE_DIR, "gemma-3-4b-it-qat-q4_0.gguf")

def check_huggingface_cli():
    """Check if Hugging Face CLI is installed"""
    try:
        subprocess.run(["huggingface-cli", "--version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def install_huggingface_cli():
    """Install Hugging Face CLI"""
    print("Installing Hugging Face CLI...")
    subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub[cli]"])

def login_to_huggingface():
    """Login to Hugging Face"""
    print("You need to log in to Hugging Face to download this model.")
    print("You will be prompted to enter your Hugging Face token.")
    print("You can find your token at https://huggingface.co/settings/tokens")
    subprocess.run(["huggingface-cli", "login"])

def download_model():
    """Download model using Hugging Face CLI"""
    model_id = "google/gemma-3-4b-it-qat-q4_0-gguf"
    
    if os.path.exists(MODEL_PATH):
        print(f"Model file already exists at {MODEL_PATH}")
        response = input("Do you want to download it again? (y/n): ")
        if response.lower() != 'y':
            print("Skipping download. You can now run the bot with: python bot.py")
            return
    
    print(f"Downloading {model_id}...")
    subprocess.run([
        "huggingface-cli", "download", 
        model_id,
        MODEL_PATH,
        "--local-dir", ".",
        "--local-dir-use-symlinks", "False"
    ])
    
    # Verify download was successful
    if os.path.exists(MODEL_PATH):
        print(f"Download complete! Model saved to {MODEL_PATH}")
        print("You can now run the bot with: python bot.py")
    else:
        print("Download failed. Please try again or check your Hugging Face permissions.")

if __name__ == "__main__":
    # Check if Hugging Face CLI is installed
    if not check_huggingface_cli():
        install_huggingface_cli()
    
    # Login to Hugging Face
    login_to_huggingface()
    
    # Download the model
    download_model()