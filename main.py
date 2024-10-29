import os
import pandas as pd
import numpy as np
from PIL import Image
import cv2
import logging
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Define the data and output directories
data_dir = "C:/Users/SEC/OneDrive/Desktop/kk/data"
output_dir = "C:/Users/SEC/OneDrive/Desktop/kk/output"

# Set up logging
logging.basicConfig(filename='processing_errors.log', level=logging.ERROR)

# Image and Signal File Extensions
image_extensions = (".jpg", ".png")
csv_extension = ".csv"

# Function to process images efficiently with OpenCV
def process_image(image_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Read image as grayscale using OpenCV
        if img is None:
            raise ValueError(f"Image {image_path} could not be loaded.")
        output_path = os.path.join(output_dir, os.path.basename(image_path))
        cv2.imwrite(output_path, img)  # Save the processed grayscale image
        print(f"Processed image: {output_path}")
    except Exception as e:
        error_message = f"Error processing image {image_path}: {e}"
        print(error_message)
        logging.error(error_message)

# Function to process signals with chunking for large files
def process_signal(signal_path):
    try:
        chunksize = 10000  # Process 10,000 rows at a time to handle large files
        for chunk in pd.read_csv(signal_path, chunksize=chunksize):
            if "signal" in chunk.columns:
                chunk["filtered_signal"] = apply_filter(chunk["signal"].values)
                save_path = os.path.join(output_dir, os.path.basename(signal_path))
                chunk.to_csv(save_path, mode='a', header=not os.path.exists(save_path), index=False)
            else:
                raise KeyError(f"Column 'signal' not found in {signal_path}")
        print(f"Processed signal: {signal_path}")
    except Exception as e:
        error_message = f"Error processing signal {signal_path}: {e}"
        print(error_message)
        logging.error(error_message)

# Simple moving average filter
def apply_filter(signal, window_size=5):
    return np.convolve(signal, np.ones(window_size) / window_size, mode='same')

# Main function to handle parallel processing and progress tracking
def main():
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # List all files in the data directory
    all_files = os.listdir(data_dir)
    
    # Separate image and signal files
    image_files = [f for f in all_files if f.lower().endswith(image_extensions)]
    signal_files = [f for f in all_files if f.endswith(csv_extension)]
    
    # Use parallel processing for large datasets
    with ThreadPoolExecutor() as executor:
        # Process images in parallel with progress tracking
        for _ in tqdm(executor.map(lambda f: process_image(os.path.join(data_dir, f)), image_files), 
                      total=len(image_files), desc="Processing Images"):
            pass
        
        # Process signals in parallel with progress tracking
        for _ in tqdm(executor.map(lambda f: process_signal(os.path.join(data_dir, f)), signal_files), 
                      total=len(signal_files), desc="Processing Signals"):
            pass
    
    print("All files processed successfully.")

if __name__ == "__main__":
    main()
