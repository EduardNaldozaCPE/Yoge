# Yoge - A Yoga Training Aid App

A remastering of my university thesis paper on 'Yoga Training Aid via Pose Estimation' by turning it into a native application instead of a web app.
This project also doubles as an exercise on The Producer - Consumer Problem and Inter-Process Communication between programmes written in different languages (Python & C++).

# Objective
We aim to create an application that is composed of different processes and services which are written in different languages.
 - REST API - Create an interface to process (CRUD) user data in a database. 
 - Interprocess Communication - Using Named Pipes to seamlessly integrate a Python process with the front-end UI.
 - Native Application Development - Dip our toes in creating native Windows applications using the .NET framework 

# Stack
Using a microservices architecture, the appliation will include two REST APIs that the application will interface with. One for he Pose Estimation Service, and another for the Scores Database Service.

|Technology|Name|
|--|--|
| Pose Estimation | MediaPipe PoseLandmarker Solution (Python) |
| Interprocess Communication | Named Pipes |
| Native App UI | Electron ~Windows Presentation Foundation (.NET)~ |
| Scores API | ExpressJS (NodeJS) |
| Scores Database | SQLite |

## Communication Between Python and Node
![image](./docs/archi.drawio.png)