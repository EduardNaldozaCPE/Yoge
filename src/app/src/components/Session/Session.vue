<script setup lang="ts">
    import DoneModal from './DoneModal.vue';
    import { Pose, PoseListState, Score } from '../../interface';
    import { onMounted, ref, Ref } from 'vue';
    // Icons
    import loadingPng from '../../../assets/loading.png';
    // SVGs
    import camSvg from '../../../assets/svg/camera.svg';
    import pauseSvg from '../../../assets/svg/pause.svg';
    // Thumbs
    import UpwardSolute from '../../../assets/guides/1_02_UpwardSolute.png';

    const props = defineProps(['sessionDetails']);
    // const currentPose: Ref<Pose | null> = ref(null);
    
    let currentDevice : number = props.sessionDetails.currentDevice;
    let isRecording = false;
    let showFeed = false;
    let isSessionDone : Ref<boolean> = ref(false);
    let finalScore : Ref<number> = ref(0);
    let currentStep = 0;
    var currentScore : string = "0.0";
    var poseListState : Array<PoseListState> = [];

    // landmarkerAPI Flow:
    //  .run()  -> .onSession() -> .onStatus()
    //                          -> .onFrame()
    //                          -> .onNextPose()

    onMounted( async ()=>{
        // 1. Get all the poses
        let poses : Array<Pose> = await window.landmarkerAPI.getPoses(props.sessionDetails.sequenceId);
        let poseIds : Array<string> = [];

        // 2. Fill Pose Table
        const poseTableBody = document.getElementById('pose-table-body');
        poseTableBody!.innerHTML = "";
        for (let i = 0; i < poses.length; i++) {
            let poseId = "poseScore-".concat((i+1).toString());
            let row = document.createElement('tr');
            row.id = `pose-${i+1}`;
            let poseNameRow =  document.createElement('td');
            poseNameRow.id = `poseName-${i+1}`;
            poseNameRow.textContent = poses[i]["poseName"];
            row.appendChild(poseNameRow);
            let poseScoreRow =  document.createElement('td');
            poseScoreRow.id = poseId;
            poseScoreRow.textContent = '-';
            row.appendChild(poseScoreRow);

            poseTableBody!.appendChild(row);
            poseIds.push(poseId);
        }

        // 3. Set the state of each pose.
        for (let i=0; i<poseIds.length; i++) {
            poseListState.push({
                step: poseIds[i],
                poseName: poses[i]["poseName"],
                score: -1,
                weight: poses[i]["wght"]
            });
        } 
    });

    
    window.landmarkerAPI.onStatus(
        // Landmarker ran successfully. Show the feed.
        ()=> {
            console.log("onStatus: Success");
            let camSwitchBtn  = document.getElementById('live-camswitch')!;
            let liveFeed = document.getElementById('live-feed')!;
            liveFeed.style.opacity = "1";
            showFeed = true;
            camSwitchBtn.removeAttribute("disabled");
            resetVars();
        },
        // Landmarker failed to run. Reset to DeviceID 0 then re-run.
        ()=> {
            console.log("onStatus: Failed. Restarting...");
            let camSwitchBtn  = document.getElementById('live-camswitch')!;
            let liveFeed = document.getElementById('live-feed')!;
            liveFeed.style.opacity = "0.2";
            currentDevice = 0;
            window.landmarkerAPI.restart(
                props.sessionDetails.userId, 
                props.sessionDetails.sequenceId,
                currentDevice
            );
            camSwitchBtn!.setAttribute("disabled", "true");
        }
    );

    
    window.landmarkerAPI.enableRestart(
        props.sessionDetails.userId, 
        props.sessionDetails.sequenceId,
        ()=>{
            console.log("Rerunning landmarker...");
        }
    );
    
    window.landmarkerAPI.onFrame((imgStr:string)=>{
        if (!showFeed) return;
        let liveFeed  = document.getElementById('live-feed')!;
        liveFeed.setAttribute("src", imgStr);
    });

    
    window.landmarkerAPI.onNextPose(()=>{
        let poseTable = document.getElementById("pose-table")!;
        let currentScrollTop = poseTable.scrollTop;
        if (currentStep > 0)
            poseListState[currentStep-1].score = parseFloat(currentScore);
        poseTable.scrollTop = currentScrollTop!+30;
        currentStep++;
        console.log("currentStep = "+currentStep);
    });

    window.landmarkerAPI.onSessionDone(()=>{
        isRecording = false;
        let fScore = 0;
        for (let i = 0; i < poseListState.length; i++) {
            fScore += poseListState[i].score * (poseListState[i].weight * 0.01);
        }
        finalScore.value = fScore;
        isSessionDone.value = true;
    });

    // Scoring
    let ooga = setInterval(async () => {
        if (!isRecording)
            return;

        const widgetScore = document.getElementById('widget-score')!;
        let score: Score = await window.landmarkerAPI.getScore();
        
        let joints = ["leftElbow", "rightElbow", "leftKnee", "rightKnee", "leftShoulder", "rightShoulder", "leftHip", "rightHip"];
        let totalScore = 0.0;

        try {
            // Average all joints' scores. (TODO: Account for score weights)
            for (let [key, value] of Object.entries(score)) {
                if (joints.includes(key)) {
                    totalScore += value;
                    totalScore = totalScore/joints.length;
                }
            }
        } catch (e) {
            if (e instanceof TypeError) return;
            else console.log(e);
        }

        // Show the score in the widget
        currentScore = totalScore.toFixed(2);
        widgetScore!.innerText = `${totalScore.toFixed(2)}%`;

        // Show the score in the pose-list table row
        if (currentStep > 0) {
            document.getElementById(poseListState[currentStep-1].step)!.innerText = currentScore;
        }
    }, 1000);


    // Functions
    function switchCamera() {
        const liveFeed      = document.getElementById('live-feed')!;
        const camSwitchBtn  = document.getElementById('live-camswitch')!;
        camSwitchBtn.setAttribute("disabled", "true");
        liveFeed.setAttribute("src", loadingPng);
        showFeed = false;
        liveFeed.style.opacity = "0.2";
        currentDevice++;
        window.landmarkerAPI.restart(
            props.sessionDetails.userId, 
            props.sessionDetails.sequenceId,
            currentDevice
        );
    }

    function togglePlay() {
        if (isRecording)
            window.landmarkerAPI.pause();
        else
            window.landmarkerAPI.play();
        isRecording = !isRecording;
    }

    function resetVars() {
        document.getElementById("pose-table")!.scrollTop = 0;
    }

    function cleanup() {
        clearInterval(ooga);
    }
</script>

<template>
    <section id="app-title-bar"></section>
    <section id="app-content">
        <section id="feed-section" class="container">
            <button id="live-camswitch" @click="switchCamera()" disabled>
                <img :src="camSvg" alt="change-cam" width="40px">
            </button>
            <img id="live-guide" :src="UpwardSolute" alt="guide" width="250px">
            <img id="live-feed" :src="loadingPng" width="100%">
        </section>
        <section id="state-section" class="container">
            <div id="state-header">
                <button id="back-btn" class="menu-btn" @click="$emit('stopSession'); cleanup();">Back</button>
                <div id="state-header-text">
                    <div class="proficiency-indicator" proficiency="beginner"></div>
                </div>
            </div>
            <div id="control-widget" @click="togglePlay()">
                <img id="pause-btn" :src="pauseSvg" width="40px">
                <h1 id="widget-score">START</h1>
                <div id="control-info">
                    <p id="pose-name">Upward Salute</p>
                    <p id="breaths" class="colour-accent">1 Breath/s</p>
                </div>
            </div>
            <div class="tableFixHead" id="pose-table">
                <table>
                    <thead>
                        <tr>
                            <th>Pose Name</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody id="pose-table-body">
                    </tbody>
                </table>
            </div>
            <!-- <button id="finish-btn" class="menu-btn" @click="$emit('stopSession')" onclick="clearInterval('ooga');" disabled>Finish</button> -->
        </section>
    </section>
    <DoneModal :score="finalScore.toFixed(2)" v-if="isSessionDone" @finish="$emit('finish')"/>
</template>

<style scoped>
    #app-content {
        display: flex;
        flex-direction: row;
    }

    #feed-section {
        box-sizing: border-box;
        flex: 1;
    }

    #live-guide {
        float: right;
        position: absolute;
        margin: 10px;
        top: 5px;
        right: 390px;
        background: #3333;
        border-radius: 0px 20px 0px 20px;
    }

    #live-camswitch {
        opacity: 1;
        cursor: pointer;
        width: 50px;
        height: 50px;
        float: left;
        position: absolute;
        padding: 10px;
        margin: 10px;
        transition: background-color 0.1s ease;
        background-color: #121212;
        border: 2px #aaa2 solid;
        border-radius: 50%;
        overflow: clip;
        img {
            margin: auto;
            width: 25px;
        }
    }
    #live-camswitch:hover {
        background-color: #222;
    }
    #live-camswitch:active {
        background-color: #333;
    }
    #live-camswitch:disabled {
        opacity: 0.2;
    }

    #live-feed {
        object-fit: contain;
        border-radius: 10px;
        width: 100%;
        height: 100%;
        transition: opacity 1s ease;
    }

    #state-section {
        box-sizing: border-box;
        gap: 20px;
        padding: 15px 20px;
        width: 380px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
    }

    #state-header {
        display: flex;
        flex-direction: column;
        align-content: left;
        width: 100%;
        gap: 25px;
    }

    #state-header-text {
        display: flex;
        flex-direction: column;
        align-content: left;
        width: 100%;
        gap: 10px;
        h1 {
            font-weight: normal;
        }
    }

    #back-btn {
        color: #ddd;
        margin-right: 20px;
        width: auto;
        align-self: baseline;
        border: 1px #3333 solid;
        border-radius: 5px;
        cursor: pointer;
    }

    #control-widget {
        cursor: pointer;
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
        height: 180px;
        width: 100%;
        justify-content: space-between;
        padding: 20px 25px;
        border-radius: 20px;
        rotate: 0deg;
        transition: rotate 0.3s ease, transform 0.2s ease, box-shadow 0.4s ease;
        background: radial-gradient(
            circle at left top, 
            #8CDC0A16 0%, 
            #3C223516 51%, 
            #70397566 100%
            );
        h1 {
            font-size: 60px;
            font-weight: bold;
        }
        p {
            font-size: 20px;
            font-weight: bold;
        }
    }
    #control-widget:hover {
        rotate: 0.8deg;
        transform: scale(1.02,1.02);
        box-shadow: inset #aaa5 0px 0px 10px;
    }

    #pause-btn {
        position: absolute;
        right: 40px;
        width: 30px;
        opacity: 0.8;
    }

    #pose-table {
        width: 100%;
        flex: 1;
    }
</style>