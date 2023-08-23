import deepspeech
import numpy as np
import pyaudio
import wave

# Load Deepspeech model
model_file_path = './DeepSpeechModels/deepspeech-0.9.3-models.pbmm'
beam_width = 500
model = deepspeech.Model(model_file_path)
model.enableExternalScorer("DeepSpeechModels/deepspeech-0.9.3-models.scorer")

# Microphone Setting
RATE = 16000
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RECORD_SECONDS = 5

# initialize pyaudio
audio = pyaudio.PyAudio()

# get sounds from microphone
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)
print("Listening...")

frames = []

for _ in range(0, int(RATE / CHUNK_SIZE * RECORD_SECONDS)):
    data = stream.read(CHUNK_SIZE)
    frames.append(data)

# close stream and pyaudio
stream.stop_stream()
stream.close()
audio.terminate()

# send to DeepSpeech
buffer = b''.join(frames)
text = model.stt(buffer)

# print text
print("You said: ", text)
input("Press Enter to exit...")