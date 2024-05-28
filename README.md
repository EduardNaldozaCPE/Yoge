# Yoge - A Yoga Training Aid App

Remastering `yogaposeestim-thesis` project  by turning it into a native application instead of a web app.

# Stack
Using a microservices architecture, the appliation will include two REST APIs that the application will interface with. One for he Pose Estimation Service, and another for the Scores Database Service.

|Technology|Name|
|--|--|
| Pose Estimation | MediaPipe PoseLandmarker Solution (Python) |
| Pose Estimation Service API | Flask (Python) |
| Scores Database | SQLite |
| Scores API | ExpressJS |
| Native App UI | .NET WPF |
