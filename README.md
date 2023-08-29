# ServiceRobot

This project is the service robot development.

# System Overview

## Database
This system use mongoDB. 
Database makes it easy to access the same data with each function.

### Launching mongoDB
After installing mongoDB, run following command.
```
mongod --dbpath /your/database/path
```

## Voice Command System
Voice Command System is a function to recognize speech and return an appropriate response.

### Setup Guide of Voice Command System
This setup guide use different Python version in each installation.
- Rasa and DeepSpeech need different version of Numpy.
    - you should be better to separate development environments
- DeepSpeech does not support versions later than Python3.8 (2023/08/23)
#### Rasa
install Rasa
```
pip install rasa
```

#### spaCy
install spaCy
```
pip install spacy
```

#### DeepSpeech
install DeepSpeech
```
pip install deepspeech
```
- If the installation fails, upgrading the pip version will solve the problem.