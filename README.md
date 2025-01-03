# Yoge - A Yoga Training Aid App

A remastering of my university thesis paper on 'Yoga Training Aid via Pose Estimation' by turning it into a native application instead of a web app.

# Objective
We aim to create an application that is composed of different processes and services which are written in different languages.
 - Image Processing - Encoding and decoding bytes in different encoding formats. And knowing when to do so and for what purpose. 
 - Interprocess Communication - Using Named Pipes to seamlessly integrate a Python process with the front-end UI.
 - REST API - Create an interface to process (CRUD) user data in a database.
 - Native Application Development - Dip our toes in creating native Windows applications. 

# Stack

>**Technologies**
>
> I am aware that MediaPIpe has a [Pose Landmarker Solution for Web](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/web_js) which would eliminate the need for the Python backend and IPC entirely, however I just planned to make this project as a sort of exercise in researching and applying IPC methods in applications.
>
> I am planning on refactoring the Python Pose Landmarker "module" to be written in C++ using the [MediaPipe Framework](https://ai.google.dev/edge/mediapipe/framework/getting_started/install) to improve performance sometime in the near future.

Using a microservices architectural pattern of sorts, the appliation will interface with a REST API for the Scores Database Module, and the Pose Estimation Module for the processing and calculation of scores.

|Technology|Name|Version|
|--|--|--|
| Pose Landmarker | MediaPipe PoseLandmarker Solution (Python) | `MediaPipe v0.10.14` |
| Native App UI | Electron & Vue (Vite) | `electron@31.1.0` |
| Database Middleware | ExpressJS (NodeJS) |  `NodeJS v20.12.2` |
| Scores Database | SQLite | - |

# Compiling

1. In Command Prompt, make sure you’re in the base directory of the project (ex. `C:\Users\<username>\source\repos\Yoge>`)
2. Make sure you are running in a python virtual environment [with pip requirements installed](https://www.notion.so/Yoge-c66f695b780848189fe7de07ef7c1bdf?pvs=21). (CMD Shows: `(venv) C:\…\Yoge>`)
3. In `src/index.js`, make sure that the `DEBUG` variable is set to `false`
4. `pyinstaller ./src/services/landmarker-service/main.py -n landmarker -i ./appicon.ico --distpath ./resources` → Bundles Landmarker module in to `resources/`
5. `npm run make` → Creates the app's executable in `out/yoge-electron-win32-x64/`

# Dev Log
Dumping all my thoughts and stuff in [Notion](https://power-magpie-0b3.notion.site/Yoge-c66f695b780848189fe7de07ef7c1bdf?pvs=4).
