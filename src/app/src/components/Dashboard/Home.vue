<script setup lang="ts">
    // import { drawGauge } from './../../shared/Gauge.js';
    import { onMounted, Ref, ref } from 'vue';
    // SVGs
    import titleblockSVG from '../../../assets/titleblock.svg';
    import playSVG from '../../../assets/play.svg';
    import pfpPNG from '../../../assets/pfpnormal.png';

    interface RecentsRow {
        sequenceName: string,
        score: number,
        date: string
    }

    const name = ref("John Doe");
    const isFirstTime = ref(false)
    const allHistory : Ref< Array<any> > = ref([]);
    const sequenceHistory : Ref< Array<any> > = ref([]);
    const recents : Ref< Array<RecentsRow> >= ref([]);
    
    onMounted(async ()=>{
        allHistory.value = await window.landmarkerAPI.getAllHistory();
        sequenceHistory.value = await window.landmarkerAPI.getHistory(allHistory.value[allHistory.value.length - 1].sequenceId);
        populateUI();
    });

  
    function populateUI() {
        var widgetTitle = document.getElementById('widget-header-title')!;
        var latest_canvas = document.getElementById('score-widget-latest');
        var best_canvas = document.getElementById('score-widget-best');
        var avg_canvas = document.getElementById('score-widget-average');
        var latest_ctx = (latest_canvas as HTMLCanvasElement).getContext('2d');
        var best_ctx = (best_canvas as HTMLCanvasElement).getContext('2d');
        var avg_ctx = (avg_canvas as HTMLCanvasElement).getContext('2d');

        if (isFirstTime.value) return;

        let latestScore = 0;
        let bestScore = 0;
        let avgScore  = 0;
        let scoreSum  = 0;
        let _scores = [];
        
        if (sequenceHistory.value.length != 0) {
            // Push History to recents array for recents table
            for (let i = 0; i < allHistory.value.length; i++) {
                recents.value.push({
                    sequenceName: allHistory.value[i].sequenceName,
                    score: allHistory.value[i].score.toFixed(2),
                    date: new Date(parseInt(allHistory.value[i].datetime)).toDateString()
                });
            }

            // Calculate Latest Sequence's Stats
            for (let i = 0; i < sequenceHistory.value.length; i++) {
                scoreSum += sequenceHistory.value[i].score;
                if (i == sequenceHistory.value.length-1) latestScore = sequenceHistory.value[i].score;
                if (sequenceHistory.value[i].score > bestScore) bestScore = sequenceHistory.value[i].score;
                _scores.push(sequenceHistory.value[i].score.toFixed(2));
            }
            avgScore = scoreSum / sequenceHistory.value.length;
        }
        

        // Show Sequence Name
        widgetTitle.innerText = allHistory.value[allHistory.value.length-1].sequenceName;
        drawGauge(latest_canvas as HTMLCanvasElement, latest_ctx!, parseFloat(latestScore.toFixed(2)), '#ddd');
        drawGauge(best_canvas as HTMLCanvasElement, best_ctx!, parseFloat(bestScore.toFixed(2)), '#ddd');
        drawGauge(avg_canvas as HTMLCanvasElement, avg_ctx!, parseFloat(avgScore.toFixed(2)), '#ddd');
    }

    function drawGauge(
        canvas: HTMLCanvasElement, 
        ctx : CanvasRenderingContext2D, 
        percentage : number, 
        colour : string
    ) {
        let startAngle  = -Math.PI / 2;
        let endAngle    = startAngle + (2 * Math.PI * percentage / 100);
        let radius      = 60;
        let lineWidth   = 20;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.beginPath();
        ctx.arc(canvas.width / 2, canvas.height / 2, radius, startAngle, 360);
        ctx.lineWidth = lineWidth;
        ctx.strokeStyle = "#fff3";
        ctx.lineCap = "round";
        ctx.stroke();
        ctx.closePath();

        ctx.beginPath();
        ctx.arc(canvas.width / 2, canvas.height / 2, radius, startAngle, endAngle);
        ctx.lineWidth = lineWidth;
        ctx.strokeStyle = colour;
        ctx.lineCap = "round";
        ctx.stroke();
        ctx.closePath();
        
        ctx.font = 'bold 45px Worksans';
        ctx.fillStyle = colour;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(percentage.toString(), canvas.width / 2, canvas.height / 2);
    }

</script>

<template>
    <div id="menu-seq-left">
        <div id="dash-header">
            <h1 id="header">Welcome, {{ name }}</h1>
            <p class="colour-accent">Let's make this day an active one.</p>
        </div>
        <div id="menu-wrapper">
            <div id="menu-stats">
                <div id="stats-latest">
                    <div class="stat-title">
                        <img :src="titleblockSVG">
                        <p>Latest Session</p>
                    </div>
                    <div id="latest-widget" @click="$emit('startSession', allHistory[allHistory.length - 1].sequenceId)">
                        <div id="widget-header">
                            <h1 id="widget-header-title"></h1>
                            <img :src="playSVG" width="20px">
                        </div>
                        <div id="widget-contents">
                            <div class="score-widget-score">
                                <canvas width="150" class="score-widget-canvas" id="score-widget-latest"></canvas>
                                <p>Latest Score</p>
                            </div>
                            <div class="score-widget-score">
                                <canvas width="150" class="score-widget-canvas" id="score-widget-best"></canvas>
                                <p>Best Score</p>
                            </div>
                            <div class="score-widget-score">
                                <canvas width="150" class="score-widget-canvas" id="score-widget-average"></canvas>
                                <p>Average Score</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div id="stats-sessions">
                    <div class="stat-title">
                        <img :src="titleblockSVG">
                        <p>Recent Sessions</p>
                    </div>
                    <div class="tableFixHead">
                        <table>
                            <thead>
                                <tr>
                                    <th>Sequence Name</th>
                                    <th>Score</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody id="history-table-body">
                                <tr v-for="session in recents">
                                    <td>{{ session.sequenceName }}</td>
                                    <td>{{ session.score }}</td>
                                    <td>{{ session.date }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div id="menu-profile">
                <img :src="pfpPNG" width="100">
                <div id="profile-nameplate">
                    <p id="profile-name">{{ name }}</p>
                    <p id="profile-nickname">Nickname</p>
                </div>
                <div id="profile-deets">
                    <div class="deets-row">
                        <p id="deets-title">Age</p>
                        <p id="deets-value">32</p>
                    </div>
                    <div class="deets-row">
                        <p id="deets-title">Experience Level</p>
                        <p id="deets-value">Beginner</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
#menu-wrapper {
  display: flex; 
  align-items: stretch;
  flex: 1;
  gap: 25px;
}

#menu-stats {
    display: flex;
    flex-direction: column;
    gap: 25px;
    flex: 1;
    justify-content: space-evenly;
}

#stats-latest {
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: center;
}

.stat-title {
    display: flex;
    flex-direction: row;
    gap: 5px;
    width: 100%;
}

#latest-widget {
    cursor: pointer;
    background-color: #6F4699;
    border-radius: 15px;
    padding: 20px 40px;
    gap: 30px;
    width: 500px;
    display: flex;
    flex-direction: column;
    transition: background-color 0.1s ease, rotate 0.5s ease, transform 0.2s ease;
    rotate: 0deg;
}
#latest-widget:hover {
    background-color: #804eb1;
    box-shadow: #5555 0px 0px 10px;
    rotate: 0.5deg;
    transform: scale(1.02, 1.02);
}

#widget-header {
    display: flex;
    width: -webkit-fill-available;
    justify-content: space-between;
    h1 {
        font-weight: normal;
        font-size: 15px;
    }
}

#widget-contents {
    display: flex;
    flex-direction: row;
    justify-content: space-evenly;
    canvas {
        border-radius: 10px;
    }
}

#stats-sessions {
    display: flex;
    flex-direction: column;
    gap: 10px;

    thead {
        height: 30px;
        color: var(--accent-colour);
    };

    tbody {
        height: 120px;
        overflow-y: auto;
    };
}

#menu-profile {
  width: 250px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 100px 0px;

  background: var(--container-colour);
  box-shadow: #00000033 0px 0px 10px;
  border-radius: 10px;
}

#profile-nameplate {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;

  #profile-name {
    font-size: 15px;
  };
  
  #profile-nickname {
    font-size: 12px;
    color: var(--accent-colour)
  };
}
.deets-row {
  display: flex;
  flex-direction: row;
  gap: 10px;
  #deets-title {
    color: var(--accent-colour);
    width: 86px;
  }
}

</style>