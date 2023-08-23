# ServiceRobot

This project is part of the service robot development.
This repository containts the source code for Voice Command of service robot.

## System Overview

## Setup Guide
This setup guide use different Python version in each installation.
- Rasa and DeepSpeech need different version of Numpy.
    - you should be better to separate development environments
- DeepSpeech does not support versions later than Python3.8 (2023/08/23)
### Rasa
install Rasa
```
pip install rasa
```

### spaCy
install spaCy
```
pip install spacy
```

### DeepSpeech
install DeepSpeech
```
pip install deepspeech
```
- If the installation fails, upgrading the pip version will solve the problem.