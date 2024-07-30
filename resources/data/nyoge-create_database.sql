BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "current_state" (
	"id"	INTEGER,
	"type"	TEXT,
	"body"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "pose" (
	"poseId"	INTEGER,
	"sequenceId"	INTEGER DEFAULT 0,
	"stepNum"	INTEGER,
	"poseName"	TEXT,
	"targetLeftElbow"	NUMERIC,
	"targetRightElbow"	NUMERIC,
	"targetLeftKnee"	NUMERIC,
	"targetRightKnee"	NUMERIC,
	"targetLeftShoulder"	NUMERIC,
	"targetRightShoulder"	NUMERIC,
	"targetLeftHip"	NUMERIC,
	"targetRightHip"	NUMERIC,
	"duration"	NUMERIC,
	"wght"	NUMERIC,
	PRIMARY KEY("poseId"),
	FOREIGN KEY("sequenceId") REFERENCES "sequence"("sequenceId") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "score" (
	"scoreId"	INTEGER,
	"sessionId"	INTEGER,
	"step"	INTEGER,
	"leftElbow"	NUMERIC,
	"rightElbow"	NUMERIC,
	"leftKnee"	NUMERIC,
	"rightKnee"	NUMERIC,
	"leftShoulder"	NUMERIC,
	"rightShoulder"	NUMERIC,
	"leftHip"	NUMERIC,
	"rightHip"	NUMERIC,
	PRIMARY KEY("scoreId" AUTOINCREMENT),
	FOREIGN KEY("sessionId") REFERENCES "session" ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "sequence" (
	"sequenceId"	INTEGER,
	"sequenceName"	TEXT,
	"poseNum"	INTEGER,
	"tags"	TEXT,
	"peakPose"	INTEGER,
	"difficulty"	TEXT,
	PRIMARY KEY("sequenceId")
);
CREATE TABLE IF NOT EXISTS "session" (
	"sessionId"	INTEGER,
	"userId"	INTEGER,
	"sequenceId"	INTEGER NOT NULL,
	PRIMARY KEY("sessionId" AUTOINCREMENT),
	FOREIGN KEY("userId") REFERENCES "user" ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "user" (
	"userId"	INTEGER,
	"username"	TEXT,
	"averageScore"	NUMERIC DEFAULT (0.0),
	"bestScore"	NUMERIC DEFAULT (0.0),
	"bestSequenceId"	INTEGER,
	PRIMARY KEY("userId" AUTOINCREMENT)
);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (1,1,1,'Prayer Pose',325.7289619,286.7764138,180,180,0,0,172.5652274,174.2249081,4,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (2,1,2,'Upward Solute',189.2543928,184.6207853,180,180,0,0,169.5731042,171.8436228,4,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (3,1,3,'Standing Forward Fold',207.0365057,211.1990789,180,180,0,0,330.0205866,330.0495943,8,8);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (4,1,4,'Low Lunge',196.6973788,203.1634519,180,180,0,0,316.6786257,310.6521015,8,8);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (5,1,5,'Plank Pose',191.4248693,192.6490851,179.0665453,176.0764059,0,0,182.728874,184.9840967,4,8);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (6,1,6,'Chaturanga',303.1828598,294.1131289,178.1170724,177.705973,0,0,182.9627792,182.9527065,4,8);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (7,1,7,'Cobra Pose',188.7129884,188.494481,169.2262048,165.796373,0,0,138.0742693,140.9938684,4,8);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (8,1,8,'Downward Dog',185.7390733,186.3611989,180,180,0,0,274.083141,274.8590369,20,22);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (9,1,9,'Low Lunge',196.6973788,203.1634519,180,180,0,0,316.6786257,310.6521015,8,8);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (10,1,10,'Standing Forward Fold',207.0365057,211.1990789,180,180,0,0,330.0205866,330.0495943,8,12);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (11,1,11,'Upward Solute',189.2543928,184.6207853,180,180,0,0,169.5731042,171.8436228,4,4);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (12,1,12,'Prayer Pose',325.7289619,286.7764138,180,180,0,0,172.5652274,174.2249081,4,4);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (13,2,1,'Salutation Pose',325.7289619,286.7764138,180,180,0,0,172.5652274,174.2249081,4,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (14,2,2,'Raised Arm Backbend Pose',222.5040717,214.8514357,180,180,0,0,159.325952,165.1257987,4,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (15,2,3,'Hand to Foot Posture',207.0365057,211.1990789,180,180,0,0,330.0205866,330.0495943,8,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (16,2,4,'Equestrian Pose (Left)',183.2342433,188.2964538,132.0409465,83.81284308,0,0,195.1974734,324.4597588,8,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (17,2,5,'Plank Pose',191.4248693,192.6490851,179.0665453,176.0764059,0,0,182.728874,184.9840967,4,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (18,2,6,'Salutation with eight limbs',297.801308,291.2350886,148.2506178,146.0344858,0,0,207.8264332,204.5578321,4,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (19,2,7,'Cobra Pose',188.7129884,188.494481,169.2262048,165.796373,0,0,138.0742693,140.9938684,4,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (20,2,8,'Downward Dog',185.7390733,186.3611989,180,180,0,0,274.083141,274.8590369,20,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (21,2,9,'Equestrian Pose (Right)',188.3379669,188.031164,142.6537012,68.88008232,0,0,188.0915278,330.9199111,8,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (22,2,10,'Hand to Foot Posture',207.0365057,211.1990789,180,180,0,0,330.0205866,330.0495943,8,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (23,2,11,'Raised Arm Backbend Pose',222.5040717,214.8514357,180,180,0,0,159.325952,165.1257987,4,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (24,2,12,'Salutation Pose',325.7289619,286.7764138,180,180,0,0,172.5652274,174.2249081,4,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (25,2,13,'Airplane Pose II',152.417304,151.1662462,275.4740029,193.5649711,0,0,18.4718215,161.4483696,48,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (26,2,14,'Airplane Pose II (Other Side)',222.1525567,210.2266719,170.3864923,73.90512855,0,0,195.2041511,341.24779,48,5);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (27,2,15,'Bowing Yoga Mudra',180.5173204,174.3427571,26.50203037,28.78201753,0,0,327.4454673,328.6086397,48,6);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (28,2,16,'Boat Pose',202.0987961,206.6801031,180,180,0,0,289.4500989,305.8616405,64,6);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (29,2,17,'Both Big Toe Pose',185.5651109,193.2357693,180,180,0,0,313.705826,307.7681379,48,6);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (30,2,18,'Camel Pose',169.559758,173.4884192,72.02899299,78.61466322,0,0,129.3940375,131.7773367,48,6);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (31,2,19,'Cat Pose Variation Knee',194.9269696,203.8134942,55.42728406,101.2536583,0,0,302.415431,261.6231563,48,6);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (32,3,1,'Seated Cow Pose',169.1371509,189.144219,336.2996467,26.46828723,0,0,81.48602621,261.8276562,60,10);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (33,3,2,'Revolved Easy Pose',164.5812613,167.3064612,332.5051946,30.23127516,0,0,90.4889475,235.969426,60,10);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (34,3,3,'Revolved Easy Pose (Other Side)',221.5926515,209.8710753,338.4564062,26.2896383,0,0,89.61241131,257.7168852,60,10);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (35,3,4,'Easy Pose Side Bend',139.5895308,196.059351,335.5305727,21.19479435,0,0,83.69068166,262.6272805,30,11);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (36,3,5,'Easy Pose Side Bend (Other Side)',175.9111786,201.9948404,340.8645654,15.73730241,0,0,91.80900425,286.688938,30,11);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (37,3,6,'Easy Pose Variation Side',164.1907583,237.8306635,340.4136649,25.38727258,0,0,110.600929,306.6038109,30,12);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (38,3,7,'Easy Pose Variation Side Bend',144.1718495,233.7464314,335.0791698,15.90263329,0,0,131.6909775,333.2992157,30,12);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (39,3,8,'Easy Pose Variation Side (Other Side)',133.9631704,197.7018409,340.7162483,13.1686452,0,0,65.63662512,259.3543866,30,12);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (40,3,9,'Easy Pose Variation Side Bend (Other Side)',120.7509087,199.6773481,341.1175211,20.82995175,0,0,37.53110266,234.332435,30,12);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (41,4,1,'Child Pose',170.8073692,181.4035025,36.87032367,36.28308938,0,0,331.7071858,328.1820532,32,12);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (42,4,2,'Locust Pose',179.612014,171.0766478,165.9437482,165.520432,0,0,138.2351086,131.4126442,48,12);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (43,4,3,'Downward Dog',185.7390733,186.3611989,180,180,0,0,274.083141,274.8590369,48,13);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (44,4,4,'Warrior Pose I',195.768813,193.1543507,73.27227186,141.051125,0,0,267.9348427,141.4607612,48,13);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (45,4,5,'Reverse Warrior Pose',304.4864288,295.9832904,41.07107861,30.96284753,0,0,326.6662792,327.8497338,48,13);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (46,4,6,'Extended Triangle Pose',189.3955746,146.5662653,103.6989341,177.0616076,0,0,254.7060451,107.3304162,32,13);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (47,4,7,'Intense Leg Stretch Pose',192.4103021,166.9897658,149.0086626,167.7295229,0,0,310.5378433,183.8742604,64,13);
INSERT INTO "pose" ("poseId","sequenceId","stepNum","poseName","targetLeftElbow","targetRightElbow","targetLeftKnee","targetRightKnee","targetLeftShoulder","targetRightShoulder","targetLeftHip","targetRightHip","duration","wght") VALUES (48,4,8,'Garland Pose',238.7597283,124.1989529,165.2294046,202.3799291,0,0,328.6305419,22.39476084,48,12);
INSERT INTO "sequence" ("sequenceId","sequenceName","poseNum","tags","peakPose","difficulty") VALUES (1,'General Fitness Sequence (Sun Salutation A)',12,'stretching, warm-up','Downward Dog','Beginner');
INSERT INTO "sequence" ("sequenceId","sequenceName","poseNum","tags","peakPose","difficulty") VALUES (2,'Core Strength Yoga Sequence',19,'core strength, spine','Boat Pose','Intermediate');
INSERT INTO "sequence" ("sequenceId","sequenceName","poseNum","tags","peakPose","difficulty") VALUES (3,'Flexibility Sequence',9,'flexibility','Easy Pose Variation Side Bend','Intermediate');
INSERT INTO "sequence" ("sequenceId","sequenceName","poseNum","tags","peakPose","difficulty") VALUES (4,'Weight Loss Sequnce',8,'weight-loss, warm-up','Intense Leg Stretch Pose','Beginner');
COMMIT;
