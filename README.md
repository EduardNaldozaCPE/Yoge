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
| Pose Landmarker | MediaPipe PoseLandmarker Solution (Python) |
| Interprocess Communication Method | Named Pipes (Windows API) |
| Native App UI | Electron ~Windows Presentation Foundation (.NET)~ |
| Database Middleware | ExpressJS (NodeJS) |
| Scores Database | SQLite |

**Note:**
I am aware that MediaPIpe has a (Pose Landmarker Solution for Web)[https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/web_js] which would eliminate the need for the Python backend and IPC entirely, however I just planned to make this project as a sort of exercise in researching and applying IPC methods in applications. I am planning on refactoring the Python Pose Landmarker "module" to be written in C++ using the [MediaPipe Framework](https://ai.google.dev/edge/mediapipe/framework/getting_started/install) somewhere in the near future.

## Communication Between Python and Node
![image](./docs/archi.drawio.png)
