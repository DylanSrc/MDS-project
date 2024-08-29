import os
import numpy as np
import matplotlib.pyplot as plt
from obspy import read
from scipy.signal import spectrogram

def load_seismic_data(directory, segment_length=16384):
    all_data = []
    print(f"Reading data from directory: {directory}")
    for filename in os.listdir(directory):
        if filename.endswith(".mseed"):
            filepath = os.path.join(directory, filename)
            print(f"Reading file: {filepath}")
            stream = read(filepath)
            for tr in stream:
                data = tr.data
                if len(data) >= segment_length:
                    # Truncate data to the specified segment length
                    data = data[:segment_length]
                    all_data.append(data)
                    print(f"Data length: {len(data)}")
    return np.array(all_data)

def generate_spectrograms(data, segment_length):
    num_segments = data.shape[0]
    print(f"Total segments: {num_segments}")
    
    plt.figure(figsize=(15, 15))
    for i in range(min(num_segments, 9)):  # Display the first 9 segments
        f, t, Sxx = spectrogram(data[i], fs=100.0, nperseg=256, noverlap=128)  # Adjust nperseg and noverlap
        plt.subplot(3, 3, i + 1)
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title(f'Spectrogram Segment {i}')
        plt.colorbar(label='Power/Frequency (dB/Hz)')
    
    plt.tight_layout()
    plt.show()

def main():
    data_path = r'C:\Users\84278\Desktop\codefile\C++\AM.R50D6'  # Update this path to your mseed directory
    segment_length = 16384  # Adjust segment length for better frequency resolution
    
    data = load_seismic_data(data_path, segment_length)
    
    if data.size == 0:
        print("No data loaded. Exiting.")
        return
    
    print(f"Original data size: {data.shape}")
    
    # Normalize data
    data_mean = np.mean(data)
    data_std = np.std(data)
    data = (data - data_mean) / data_std
    print(f"Data mean: {data_mean}, Data std: {data_std}")
    print(f"Data mean after normalization: {np.mean(data)}, Data std after normalization: {np.std(data)}")
    
    # Generate and plot spectrograms
    generate_spectrograms(data, segment_length)

if __name__ == "__main__":
    main()
