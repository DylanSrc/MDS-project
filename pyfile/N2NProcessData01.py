import numpy as np
import os
import glob
from obspy import read
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

# Data Preparation
def load_seismic_data(data_path):
    files = glob.glob(os.path.join(data_path, '*.mseed'))
    if not files:
        print("No MSEED files found in the specified directory.")
        return np.array([])

    data = []
    for file in tqdm(files, desc="Loading seismic data"):
        st = read(file)
        for tr in st:
            data.append(tr.data)
    data = np.concatenate(data, axis=0)
    return data

def partial_fit_scaler(data, scaler, batch_size):
    num_batches = len(data) // batch_size + 1
    for i in tqdm(range(num_batches), desc="Fitting scaler"):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(data))
        batch_data = data[start_idx:end_idx].reshape(-1, 1)
        scaler.partial_fit(batch_data)

def transform_data(data, scaler, batch_size):
    data_normalized = np.empty_like(data, dtype=np.float64)
    num_batches = len(data) // batch_size + 1
    for i in tqdm(range(num_batches), desc="Transforming data"):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(data))
        batch_data = data[start_idx:end_idx].reshape(-1, 1)
        data_normalized[start_idx:end_idx] = scaler.transform(batch_data).flatten()
    return data_normalized

def normalize_data(data, batch_size=100000):
    scaler = StandardScaler()
    partial_fit_scaler(data, scaler, batch_size)
    data_normalized = transform_data(data, scaler, batch_size)
    return data_normalized, scaler

# Data Segmentation
def segment_data(data, segment_length, height):
    segments = []
    segment_size = segment_length * height
    for i in tqdm(range(0, len(data) - segment_size + 1, segment_size), desc="Segmenting data"):
        segment = data[i:i + segment_size].reshape((height, segment_length, 1))
        segments.append(segment)
    segments = np.array(segments)
    return segments

# Main function
if __name__ == "__main__":
    data_path = r'C:\Users\84278\Desktop\codefile\C++\AM.R50D6'  # Seismic data path
    segment_length = 128  # Segment length
    height = 128  # Segment height
    normalization_batch_size = 100000  # Normalization batch size

    # Load and normalize data
    data = load_seismic_data(data_path)
    if data.size == 0:
        print("No data loaded. Exiting.")
        exit()
    data, scaler = normalize_data(data, normalization_batch_size)
    print(f"Original data size: {data.shape}")

    # Data segmentation
    segments = segment_data(data, segment_length, height)
    print(f"Segmented data size: {segments.shape}")

    # Save segments to disk
    np.save('segments.npy', segments)
    print("Data preprocessing completed.")
