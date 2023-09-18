let mediaRecorder;
let audioChunks = [];

// 音声入力を収録してサーバーに送信する関数
function recordAndSend(audioBlob) {
    let formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');

    // 音声データをテキストに変換
    fetch('http://localhost:5001/audio_to_text', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(text => {
        // テキストデータをRasaサーバーに送信して応答を取得
        let parsedText = JSON.parse(text).text;
        return fetch('http://localhost:5001/get_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: parsedText })
        });
    })
    .then(response => response.text())
    .then(responseText => {
        // convert Text to Audio
        document.getElementById("rasaReply").textContent = "Rasa Reply: " + responseText;
        if (responseText.includes("ask_location:")) {
            // Wait for user's "yes" or "no" response
            // Here you might want to show some UI indication to the user to respond
            // For simplicity, we'll just proceed to record the user's response
            stopRecording(); // Stop any current recording
            startRecording(); // Start recording user's response
        } else {
        return fetch('http://localhost:5001/text_to_audio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: responseText })
        });
    }
})
    .then(response => response.blob())
    .then(audioBlob => {
        // 音声応答を再生
        let audio = new Audio(URL.createObjectURL(audioBlob));
        audio.play();
    });
}

function startRecording() {
    const streamPromise = navigator.mediaDevices.getUserMedia({ audio: true });

    streamPromise.then(stream => {
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            audioChunks = [];
            recordAndSend(audioBlob);  // Blobを関数に渡す
        };

        mediaRecorder.start();
    })
    .catch(err => {
        console.error("Error accessing the microphone:", err);
    });
    document.getElementById("recordingStatus").textContent = "Recording...";

}

function stopRecording() {
    document.getElementById("recordingStatus").textContent = "Not recording";
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        // Handle the user's response to the location question
        handleUserResponse(new Blob(audioChunks, { type: 'audio/webm' }));
    }
}

function handleUserResponse(audioBlob) {
    let formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');

    fetch('http://localhost:5001/handle_user_response', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.response) {
            // Handle the response, such as playing back a confirmation message
        }
    });
}