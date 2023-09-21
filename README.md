# ServiceRobot

This project is the service robot development.

# System Overview

# How to start
clone this repository into your PC.
```
git clone https://github.com/HoYo44/ServiceRobot.git
```

Add submodule
```
git submodule init
```
```
git submodule update
```
## Database
This system use mongoDB. 
Database makes it easy to access the same data with each function.

### MongoDB
After installing MongoDB, run following command.
```
mongod --dbpath /your/database/path
```

## [Voice Command System](./VoiceCommand/VoiceCommand.md)
Voice Command System has two main functions that Voice Recognition and Text-based Chat.
The objective of this system is to provide service robots with the ability that understanding exactly what the customer is saying and appropriate responses.