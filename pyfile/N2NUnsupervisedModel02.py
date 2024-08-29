import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, concatenate
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.utils import Sequence
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
import os
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

# Define U-Net model
def unet_model(input_size=(128, 128, 1)):
    inputs = Input(input_size)
    
    # Encoding path
    conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')(pool1)
    conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    conv3 = Conv2D(128, (3, 3), activation='relu', padding='same')(pool2)
    conv3 = Conv2D(128, (3, 3), activation='relu', padding='same')(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

    conv4 = Conv2D(256, (3, 3), activation='relu', padding='same')(pool3)
    conv4 = Conv2D(256, (3, 3), activation='relu', padding='same')(conv4)
    pool4 = MaxPooling2D(pool_size=(2, 2))(conv4)

    # Bottleneck
    conv5 = Conv2D(512, (3, 3), activation='relu', padding='same')(pool4)
    conv5 = Conv2D(512, (3, 3), activation='relu', padding='same')(conv5)

    # Decoding path
    up6 = UpSampling2D(size=(2, 2))(conv5)
    up6 = Conv2D(256, (2, 2), activation='relu', padding='same')(up6)
    merge6 = concatenate([conv4, up6], axis=3)
    conv6 = Conv2D(256, (3, 3), activation='relu', padding='same')(merge6)
    conv6 = Conv2D(256, (3, 3), activation='relu', padding='same')(conv6)

    up7 = UpSampling2D(size=(2, 2))(conv6)
    up7 = Conv2D(128, (2, 2), activation='relu', padding='same')(up7)
    merge7 = concatenate([conv3, up7], axis=3)
    conv7 = Conv2D(128, (3, 3), activation='relu', padding='same')(merge7)
    conv7 = Conv2D(128, (3, 3), activation='relu', padding='same')(conv7)

    up8 = UpSampling2D(size=(2, 2))(conv7)
    up8 = Conv2D(64, (2, 2), activation='relu', padding='same')(up8)
    merge8 = concatenate([conv2, up8], axis=3)
    conv8 = Conv2D(64, (3, 3), activation='relu', padding='same')(merge8)
    conv8 = Conv2D(64, (3, 3), activation='relu', padding='same')(conv8)

    up9 = UpSampling2D(size=(2, 2))(conv8)
    up9 = Conv2D(32, (2, 2), activation='relu', padding='same')(up9)
    merge9 = concatenate([conv1, up9], axis=3)
    conv9 = Conv2D(32, (3, 3), activation='relu', padding='same')(merge9)
    conv9 = Conv2D(32, (3, 3), activation='relu', padding='same')(conv9)
    conv9 = Conv2D(2, (3, 3), activation='relu', padding='same')(conv9)
    conv10 = Conv2D(1, (1, 1), activation='sigmoid')(conv9)

    model = Model(inputs=inputs, outputs=conv10)
    return model

# Define Noise-to-Noise loss function
def n2n_loss(y_true, y_pred):
    return tf.reduce_mean(tf.square(y_pred - y_true))

# Data generator with on-the-fly augmentation
class DataGenerator(Sequence):
    def __init__(self, data, batch_size=32, augment_factor=2, noise_level=0.5):
        self.data = data
        self.batch_size = batch_size
        self.augment_factor = augment_factor
        self.noise_level = noise_level
        self.indices = np.arange(len(self.data))

    def __len__(self):
        return int(np.ceil(len(self.data) * self.augment_factor / self.batch_size))

    def __getitem__(self, index):
        start = (index * self.batch_size) % len(self.data)
        end = min(start + self.batch_size, len(self.data))
        batch_data = self.data[start:end]
        
        # Apply augmentation and add noise
        augmented_data = []
        noisy_labels = []

        for img in batch_data:
            for _ in range(self.augment_factor):
                noisy_img = img + self.noise_level * np.random.normal(loc=0.0, scale=1.0, size=img.shape)
                augmented_data.append(noisy_img)
                noisy_labels.append(img)

        augmented_data = np.array(augmented_data)
        noisy_labels = np.array(noisy_labels)
        
        # Debugging: Check for empty or None data
        if augmented_data.size == 0 or noisy_labels.size == 0:
            print(f"Empty augmented data at index {index}")

        return augmented_data, noisy_labels

    def on_epoch_end(self):
        np.random.shuffle(self.indices)

# Load your dataset
def load_data():
    # Placeholder for actual data loading logic
    # For example, load from numpy files or other sources
    # Here we generate dummy data for demonstration
    data = np.random.rand(5000, 128, 128, 1).astype(np.float32)
    return data

# Evaluation function
def evaluate_model(model, test_data, test_labels):
    predictions = model.predict(test_data)
    mse = np.mean((predictions - test_labels) ** 2)
    print(f'Mean Squared Error on test data: {mse}')
    
    psnr_values = [peak_signal_noise_ratio(test_labels[i].squeeze(), predictions[i].squeeze(), data_range=1.0) for i in range(len(test_labels))]
    ssim_values = [structural_similarity(test_labels[i].squeeze(), predictions[i].squeeze(), data_range=1.0) for i in range(len(test_labels))]
    
    mean_psnr = np.mean(psnr_values)
    mean_ssim = np.mean(ssim_values)
    
    print(f'Mean PSNR on test data: {mean_psnr}')
    print(f'Mean SSIM on test data: {mean_ssim}')
    
    return mse, mean_psnr, mean_ssim

def plot_spectrogram(data, title, filename):
    plt.figure(figsize=(10, 8))
    for i in range(min(9, len(data))):
        plt.subplot(3, 3, i + 1)
        f, t, Sxx = spectrogram(data[i].squeeze(), fs=100.0)
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title(f'Spectrogram Segment {i}')
        plt.colorbar(label='Power/Frequency (dB/Hz)')
    plt.suptitle(title)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(filename)
    plt.show()

def main():
    # Load data
    data = load_data()
    print(f'Loaded data shape: {data.shape}')

    # Sample 5% of the data for testing
    sample_size = int(0.05 * len(data))
    data = data[:sample_size]
    print(f'Sampled data shape: {data.shape}')

    # Split data into training and test sets
    split_idx = int(0.8 * len(data))
    train_data, test_data = data[:split_idx], data[split_idx:]
    
    # Create training data generator
    train_generator = DataGenerator(train_data, batch_size=32, augment_factor=2, noise_level=0.5)

    # Initialize U-Net model
    model = unet_model(input_size=(128, 128, 1))
    model.compile(optimizer=Adam(), loss=n2n_loss)

    # Define callbacks
    checkpoint = ModelCheckpoint('model.keras', save_best_only=True, monitor='loss', mode='min')
    early_stopping = EarlyStopping(monitor='loss', patience=5, mode='min')

    # Train the model
    model.fit(train_generator, epochs=10, callbacks=[checkpoint, early_stopping])

    # Load the best model
    model.load_weights('model.keras')

    # Evaluate the model
    test_labels = test_data  # In Noise2Noise, the labels are the original clean images
    evaluate_model(model, test_data, test_labels)

    # Generate and save spectrograms of original and denoised data
    plot_spectrogram(test_data, "Original Data Spectrogram", "original_spectrogram.png")
    denoised_data = model.predict(test_data)
    plot_spectrogram(denoised_data, "Denoised Data Spectrogram", "denoised_spectrogram.png")

if __name__ == '__main__':
    main()
