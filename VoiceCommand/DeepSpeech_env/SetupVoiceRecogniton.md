Setup VoiceRecognition Environment
---
### Create Virtual Environment
First, create a virtual environment with the following command.\
Windows
```
py -3.8 -m venv .\VoiceCommand\DeepSpeech_env\
```

Unix or MacOS
```
python -3.8 -m venv ./VoiceCommand/DeepSpeech_env/
```
---

Next step, activate the virtual environment. \
Windows
```
.\VoiceCommand\DeepSpeech_env\Scripts\activate
```
- If you can't activate above command, use following command.
    - ```Set-ExecutionPolicy RemoteSigned -Scope Process -force```
        - **You need to type this command every time you launch the terminal.**

Unix or MacOS
```
source ./VoiceCommand/DeepSpeech_env/Scripts/activate
```
---
After activating the virtual environment install the packages for the system requirements with the following command.
```
pip install -r ./Voice/Command/DeepSpeech_env/requirements_deepspeech.txt
```
- If the installation fails, upgrading the pip version will solve the problem.