#!/usr/bin/env python3
import os
import requests
from tqdm import tqdm

MODEL_BASE_DIR = os.path.join(os.getcwd(), "models")
os.makedirs(MODEL_BASE_DIR, exist_ok=True)
MODEL_URL = "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
MODEL_PATH = os.path.join(MODEL_BASE_DIR, "Phi-3-mini-4k-instruct-q4.gguf")


def download_file(url, destination):
    """
    Download a file from url to destination with progress bar
    """
    if os.path.exists(destination):
        print(f"Model file already exists at {destination}")
        response = input("Do you want to download it again? (y/n): ")
        if response.lower() != 'y':
            return
    
    print(f"Downloading model from {url}")
    print(f"This may take some time depending on your internet connection...")
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    
    with open(destination, 'wb') as file, tqdm(
        desc=destination,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(block_size):
            size = file.write(data)
            bar.update(size)
    
    print(f"Download complete! Model saved to {destination}")

if __name__ == "__main__":    
    download_file(MODEL_URL, MODEL_PATH)
    print("Now you can run the bot with: python bot.py")