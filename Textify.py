from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask import send_from_directory
import ngrok

import pyaudio
import time
import threading
import queue
import csv
import os

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_io as tfio
import numpy as np

from IPython.display import Audio
from scipy.io import wavfile
from keras_yamnet import params
from keras_yamnet.yamnet import YAMNet, class_names
from keras_yamnet.preprocessing import preprocess_input


# Load the model.
try:
    model = hub.load('https://tfhub.dev/google/yamnet/1')
    print("YAMNet model loaded successfully.")
except Exception as e:
    print(f"Error loading YAMNet model: {e}")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/latency_data.csv')
def download_latency_data():
    return send_from_directory(os.getcwd(), 'latency_data.csv', as_attachment=True)

@app.route('/')
def index():
    return render_template('index.html')

class SoundClassifierApp:

    def __init__(self):
        self.init_model()
        self.init_audio()
        self.queue = queue.Queue()
        self.latencies = []  # List to store latency values
        self.time_stamps = []  # List to store timestamps for the latencies
        self.start_time = None  # Initialize start_time

    def init_model(self):
        self.model = YAMNet(weights='keras_yamnet/yamnet.h5')
        self.yamnet_classes = class_names('keras_yamnet/yamnet_class_map.csv')

    def init_audio(self):
        self.audio = pyaudio.PyAudio()
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = params.SAMPLE_RATE
        self.WIN_SIZE_SEC = 0.975
        self.CHUNK = int(self.WIN_SIZE_SEC * self.RATE)
        self.MIC = None

    def stream_audio(self):
        self.start_time = time.time()  # Record the start time when streaming starts
        self.stream_stopped = False
        stream = self.audio.open(input_device_index=self.MIC,
                                 format=self.FORMAT,
                                 channels=self.CHANNELS,
                                 rate=self.RATE,
                                 input=True,
                                 frames_per_buffer=self.CHUNK)

        while not self.stream_stopped:
            # Read audio data from the stream
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            socketio.emit('audio_chunk', data)

            # Measure the time it takes to process the audio chunk
            start_time = time.time()

            # Preprocess the audio chunk
            audio_input = preprocess_input(np.frombuffer(data, dtype=np.float32), self.RATE)

            # Classify the processed audio
            prediction = self.model.predict(np.expand_dims(audio_input, 0))[0]
            classified_sound = self.get_classified_sound(prediction)

            # Track latency (time taken for classification)
            latency = time.time() - start_time
            self.latencies.append(latency)  # Add latency to the list
            self.time_stamps.append(time.time() - self.start_time)  # Time since stream started

            # Send latency data to the frontend
            socketio.emit('latency_data', latency)

            # Print the classification result
            print(f"Predicted sound class: {classified_sound} (Latency: {latency:.4f} seconds)")

            # Emit classification result to clients
            socketio.emit('classification', classified_sound)

            # Emit danger warning if harmful sound is detected
            HARMFUL_SOUNDS = {"Yell", "Children shouting", "Screaming", "Crying, sobbing", "Wail, moan", "Bark", "Hiss", "Roaring cats (lions, tigers)", "Thunderstorm", "Thunder", "Fire", "Police car (siren)", "Ambulance (siren)", "Fire engine, fire truck (siren)", "Alarm", "Alarm clock", "Siren", "Civil defense siren", "Smoke detector, smoke alarm", "Fire alarm", "Foghorn", "Slap, smack", "Smash, crash", "Train", "Explosion", "Snake"}

            if classified_sound in HARMFUL_SOUNDS:
                print("DETECTED DANGER!!!")
                socketio.emit('danger_warning', 'DANGER: Harmful sound detected!')

            # Control the data stream rate
            time.sleep(0.01)

        stream.stop_stream()

    def stop_stream(self):
        print("STREAM STOPPED")
        self.stream_stopped = True
        self.start_time = None  # Reset start time

    def callback(self, in_data, frame_count, time_info, status):
        A = preprocess_input(np.frombuffer(in_data, dtype=np.float32), self.RATE)
        prediction = self.model.predict(np.expand_dims(A, 0))[0]
        self.queue.put((A, prediction))

    def get_classified_sound(self, prediction):
        max_index = np.argmax(prediction)
        return self.yamnet_classes[max_index]

    

audio_streamer = SoundClassifierApp()


@socketio.on('start_audio_stream')
def handle_start_audio_stream():
    """Starts streaming audio to connected clients."""
    socketio.start_background_task(audio_streamer.stream_audio)

@socketio.on('stop_audio_stream')
def handle_stop_audio_stream():
    audio_streamer.stop_stream()
    audio_streamer.save_latency_data()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)    