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

## [Voice Command System](./Docs/VoiceCommand.md)
Voice Command System has two main functions that Voice Recognition and Text-based Chat.
The objective of this system is to provide service robots with the ability that understanding exactly what the customer is saying and appropriate responses.