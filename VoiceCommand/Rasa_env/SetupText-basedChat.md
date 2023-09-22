Setup Text-based Chat Environment
---
### Create Virtual Environment
First, create a virtual environment with the following command.\
Windows
```
py -3.8 -m venv .\VoiceCommand\Rasa_env\
```

Unix or MacOS
```
python -3.8 -m venv ./VoiceCommand/Rasa_env/
```
---

Next step, activate the virtual environment. \
Windows
```
.\VoiceCommand\Rasa_env\Scripts\activate
```
- If you can't activate above command, use following command.
    - ```Set-ExecutionPolicy RemoteSigned -Scope Process -force```
        - **You need to type this command every time you launch the terminal.**

Unix or MacOS
```
source ./VoiceCommand/Rasa_env/Scripts/activate
```
---
After activating the virtual environment install the packages for the system requirements with the following command.
```
pip install -r ./Voice/Command/Rasa_env/requirements_rasa.txt
```
- If the installation fails, upgrading the pip version will solve the problem.
    - Even if failed to install, you should install every libraries in manually.
```
pip install rasa spacy
```

---
Next step, you need to download model for spaCy.\
The following is example that download english model. \
```
python -m spacy download en_core_web_md
```
For more information, please check the [here](https://spacy.io/usage/models).