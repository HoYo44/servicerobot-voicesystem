import deepspeech
import numpy as np
import pyaudio

# Load Deepspeech model
model_file_path = './DeepSpeech/deepspeech-0.9.3-models.pbmm'
model = deepspeech.Model(model_file_path)

# Microphone Setting
RATE = 16000
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

# initialize pyaudio
audio = pyaudio.PyAudio()

# get sounds from microphone
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)
print("Listening...")

buffer = np.array([])

try:
    while True:
        audio_chunk = np.frombuffer(stream.read(CHUNK_SIZE, exception_on_overflow=False), dtype=np.int16)
        buffer = np.append(buffer, audio_chunk)

        # 一定の長さのデータがたまったら処理を開始
        if len(buffer) > RATE * 4: # 4s
            text = model.stt(buffer)
            print(f"Recognized:{text}")
            buffer = np.arra([]) # clear buffer

except KeyboardInterrupt:
    pass

# close stream and pyaudio
stream.stop_stream()
stream.close()
audio.terminate()