from flask import Flask, request, jsonify
import deepspeech
import requests
import io
from flask_cors import CORS
from flask import send_file
from pydub import AudioSegment
import numpy as np


app = Flask(__name__)
CORS(app)

# DeepSpeechモデルをロード
model_file_path = './DeepSpeechModels/deepspeech-0.9.3-models.pbmm'
scorer_file_path = './DeepSpeechModels/deepspeech-0.9.3-models.scorer'

model = deepspeech.Model(model_file_path)
model.enableExternalScorer(scorer_file_path)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/audio_to_text', methods=['POST'])
def audio_to_text():
    audio_file = request.files['audio']

    # Convert audio/webm to audio/wav
    audio = AudioSegment.from_file(io.BytesIO(audio_file.read()), format="webm")
    audio = audio.set_channels(1).set_frame_rate(16000)

    # Convert the audio to 16-bit PCM
    audio = audio.set_sample_width(2)  # 2 bytes = 16 bits

    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    buffer.seek(0)

    # For debugging: Save the audio to a local file
    # with open("debug_audio_16bit.wav", "wb") as f:
    #     f.write(buffer.read())
    # buffer.seek(0)

    # Convert WAV data to PCM
    # audio_wav = AudioSegment.from_wav(buffer)
    samples = np.array(audio.get_array_of_samples(), dtype=np.int16)
    # audio_data = samples.tobytes()

    # Use DeepSpeech model to get text
    text = model.stt(samples)

    return jsonify({'text': text})

@app.route('/get_response', methods=['POST'])
def get_response():
    print("Request data:", request.data)  # Raw request data
    print("Request JSON:", request.json)  # Parsed JSON data
    # Check if 'message' key exists
    if not request.json or 'message' not in request.json:
        return jsonify({"error": "Invalid request data. 'message' key not found."}), 400

    message = request.json['message']
    rasa_url = "http://localhost:5005/webhooks/rest/webhook"
    response = requests.post(rasa_url, json={"sender": "user", "message": message})
    rasa_response = response.json()

    # get reply
    reply = rasa_response[0]['text'] if rasa_response else "No response from Rasa server."
    return jsonify({"response": reply})


@app.route('/text_to_audio', methods=['POST'])
def text_to_audio():
    text = request.json['text']
    tts_url = "http://localhost:5002/api/tts"

    # send text to MozillaTTS server and get voice data
    # response = requests.post(tts_url, json={"text": text})

    # send text to MozillaTTS server and get voice data using GET method
    response = requests.get(tts_url, params={"text": text})

    # return voicedata to frontend
    return send_file(io.BytesIO(response.content), mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
