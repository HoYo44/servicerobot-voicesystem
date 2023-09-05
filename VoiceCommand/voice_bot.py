import deepspeech
import numpy as np
import pyaudio
import wave
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Load Deepspeech model
model_file_path = './DeepSpeechModels/deepspeech-0.9.3-models.pbmm'
beam_width = 500
model = deepspeech.Model(model_file_path)
model.enableExternalScorer("./DeepSpeechModels/deepspeech-0.9.3-models.scorer")

# Microphone Setting
RATE = 16000
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RECORD_SECONDS = 5

# initialize pyaudio
audio = pyaudio.PyAudio()

def send_message_to_rasa(user_message):
    url = "http://localhost:5005/webhooks/rest/webhook"
    payload = {
        "sender": "user",
        "message": user_message
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route("/transcribe", methods=["POST"])
def transcribe():
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

    # send to DeepSpeech
    buffer = np.frombuffer(b''.join(frames), dtype=np.int16)
    text = model.stt(np.array(buffer, dtype=np.int16))

    # send the transcribed text to Rasa and get the response
    rasa_response = send_message_to_rasa(text)

    # display the recognized text to the response
    response_data = rasa_response.copy()
    response_data.insert(0, {"recognized_text": text})
    
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True)
