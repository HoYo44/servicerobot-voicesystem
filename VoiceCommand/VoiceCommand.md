Voice Command System
---
Voice Command System has two main functions that Voice Recognition and Text-based Chat.
- Voice Recognition
    - pyaudio
    - DeepSpeech
- Text-based Chat
    - Rasa
    - spaCy

## Development Environment
This system uses virtual environments because each function needs to run on a different version of python. 
- Rasa and DeepSpeech need different version of Numpy.
    - You should be better to separate development environments.
- **DeepSpeech does not support versions later than Python3.8** (2023/08/23)

### Setup Environment Guide
To create virtual environments, use pip or conda, etc.
> This repository shows using pip to create virtual environments.

This setup guide assumes operation in **the root directory of this repository**.\
You can see two text files in following locations.
1. /VoiceCommand/DeepSpeech_env/requirements_deepspeech.txt
2. /VoiceCommand/Rasa_env/requirements_rasa.txt

#### [Setup VoiceRecognition Environment](./DeepSpeech_env/SetupVoiceRecogniton.md)

#### [Setup Text-based Chat Environment](./Rasa_env/SetupText-basedChat.md)