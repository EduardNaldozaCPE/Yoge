# Yoge - A Yoga Training Aid App

Remastering `yogaposeestim-thesis` project  by turning it into a native application instead of a web app.

# Objective
We aim to create an application that is composed of different processes and services which are written in different languages.
 - REST API - Create an interface to process (CRUD) user data in a database. 
 - Interprocess Communication - Using Shared Memory Mapping (mmap) to seamlessly integrate a Python process with the WPF front-end UI.
 - Native Application Development - Dip our toes in creating native Windows applications using the .NET framework 

# Stack
Using a microservices architecture, the appliation will include two REST APIs that the application will interface with. One for he Pose Estimation Service, and another for the Scores Database Service.

|Technology|Name|
|--|--|
| Pose Estimation | MediaPipe PoseLandmarker Solution (Python) |
| Interprocess Communication | Shared Memory Mapping (mmap) |
| Native App UI | QT (C++) ~Windows Presentation Foundation (.NET)~ |
| Scores API | ExpressJS (NodeJS) |
| Scores Database | SQLite |
