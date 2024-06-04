-- SQLite
CREATE TABLE IF NOT EXISTS user(
    userId INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    averageScore NUMERIC DEFAULT (0.0),
    bestScore NUMERIC DEFAULT (0.0),
    bestSequenceId INTEGER
);


CREATE TABLE IF NOT EXISTS session (
    sessionId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER REFERENCES user ON DELETE SET NULL,
    sequenceId INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS score(
    scoreId INTEGER PRIMARY KEY,
    sessionId INTEGER REFERENCES session ON DELETE SET NULL,
    timestamp INTEGER,
    leftElbow NUMERIC,
    rightElbow NUMERIC,
    leftKnee NUMERIC,
    rightKnee NUMERIC,
    leftShoulder NUMERIC,
    rightShoulder NUMERIC,
    leftHip NUMERIC,
    rightHip NUMERIC
);


CREATE TABLE IF NOT EXISTS sequence(
    sequenceId INTEGER PRIMARY KEY,
    sequenceName TEXT
);


CREATE TABLE IF NOT EXISTS pose(
    poseId INTEGER PRIMARY KEY,
    sequenceId INTEGER REFERENCES sequence ON DELETE SET NULL,
    stepNum INTEGER,
    poseName TEXT,
    targetLeftElbow NUMERIC,
    targetRightElbow NUMERIC,
    targetLeftKnee NUMERIC,
    targetRightKnee NUMERIC,
    targetLeftShoulder NUMERIC,
    targetRightShoulder NUMERIC,
    targetLeftHip NUMERIC,
    targetRightHip NUMERIC
)
;