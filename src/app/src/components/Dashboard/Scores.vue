<script setup lang="ts">
    import { onMounted, Ref, ref } from 'vue';

    const seqHistory : Ref< Array<any> > = ref([]);
    
    onMounted(async ()=>{
      updateGauges({target:{value:1}});
      updateScoreTable({target:{value:1}});
    });

    async function updateGauges(evt?: any) {
      if (!evt) return;
      seqHistory.value = await window.landmarkerAPI.getHistory(parseInt(evt.target.value));

      var latestCanvas = document.getElementById('score-widget-latest');
      var avgCanvas = document.getElementById('score-widget-average');
      var bestCanvas = document.getElementById('score-widget-best');
      var latestCtx = (latestCanvas as HTMLCanvasElement).getContext('2d');
      var bestCtx = (bestCanvas as HTMLCanvasElement).getContext('2d');
      var avgCtx = (avgCanvas as HTMLCanvasElement).getContext('2d');

      // Update Score Gauges
      let latestScore = 0.0;
      let bestScore = 0.0;
      let avgScore = 0.0;
      if (seqHistory.value.length != 0) {
        for (let i = 0; i < seqHistory.value.length; i++) {
          if (seqHistory.value[i].score > bestScore) bestScore = seqHistory.value[i].score;
          avgScore += seqHistory.value[i].score;
        }
        avgScore = avgScore / seqHistory.value.length;
        latestScore = seqHistory.value[seqHistory.value.length-1].score;
      };
      
      drawGauge(latestCanvas as HTMLCanvasElement, latestCtx!, parseFloat(latestScore.toFixed(2)), '#ddd');
      drawGauge(bestCanvas as HTMLCanvasElement, bestCtx!, parseFloat(bestScore.toFixed(2)), '#ddd');
      drawGauge(avgCanvas as HTMLCanvasElement, avgCtx!, parseFloat(avgScore.toFixed(2)), '#ddd')      
    }

    // Update Pose List Scores
    async function updateScoreTable(evt?: any) {
      if (!evt) return;

      seqHistory.value = await window.landmarkerAPI.getPoseRecords(parseInt(evt.target.value));
      console.log(seqHistory.value);
      
      let poseTable = document.getElementById("pose-table-body");
      poseTable!.innerHTML = "";

      for (let i=0; i < seqHistory.value.length; i++) {
        let newRow = document.createElement('tr');

        let poseName = document.createElement('td');
        poseName.textContent = seqHistory.value[i].poseName;
        newRow.appendChild(poseName);

        let latestScore = document.createElement('td');
        latestScore.textContent = seqHistory.value[i].latestScore.toFixed(2);
        newRow.appendChild(latestScore);

        let bestScore = document.createElement('td');
        bestScore.textContent = seqHistory.value[i].bestScore.toFixed(2);
        newRow.appendChild(bestScore);

        let avgScore = document.createElement('td');
        avgScore.textContent = seqHistory.value[i].avgScore.toFixed(2);
        newRow.appendChild(avgScore);

        poseTable?.appendChild(newRow);
      }
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
  <div id="scores-maincontent">
    <form action="#">
        <div class="custom-select">
            <select name="header-dropdown" id="header-dropdown" @change="(payload)=>{updateGauges(payload); updateScoreTable(payload)}">
                <option value="1">General Fitness Sequence (Sun Salutation A)</option>
                <option value="2">Weight Loss Sequence</option>
                <option value="3">Flexibility Sequence</option>
                <option value="4">Core Strength Sequence</option>
            </select>
        </div>
    </form>
    <div id="score-content">
        <div id="score-stats">
            <div id="score-widget">
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
            <div id="graph-widget">
                <canvas id="score-graph" width="100%" height="100%"></canvas>
            </div>
        </div>
        <div id="scores-poselist">
            <table>
                <thead>
                    <tr>
                        <th>Pose Name</th>
                        <th>Latest Score</th>
                        <th>Best Score</th>
                        <th>Average Score</th>
                    </tr>
                </thead>
                <tbody id="pose-table-body">
                    <tr>
                        <td>Pose Name</td>
                        <td>0.00</td>
                        <td>0.00</td>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <td>Pose Name</td>
                        <td>0.00</td>
                        <td>0.00</td>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <td>Pose Name</td>
                        <td>0.00</td>
                        <td>0.00</td>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <td>Pose Name</td>
                        <td>0.00</td>
                        <td>0.00</td>
                        <td>0.00</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
  </div>
</template>

<style scoped>
#scores-maincontent {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

#score-content {
  min-height: 0px;
  display: flex;
  flex-direction: column;
  padding: 10px;
}

#score-stats {
  justify-content: space-evenly;
  display: flex;
  flex-direction: column;
  padding: 10px;
}

#scores-poselist {
  flex: 1;
  overflow-y: auto;
}

#score-widget {
  display: flex;
  justify-content: space-evenly;
  flex-direction: row;
}

.score-widget-score {
  display: flex;
  flex-direction: column;
  align-items: center;

}

.score-widget-canvas {
  width: 150px;
  height: 150px;
}

.custom-select select {
  appearance: none;
  width: 100%;
  border: #333 solid 1px;
  font-size: 2rem;
  font-weight: bold;
  padding: 20px;
  cursor: pointer;
  border: 1px solid #555;
  background-color: #1a1a1a;
  border-radius: 0.25em;
  color: #fff;
  transition: background-color 0.1s linear;
}

.custom-select select:hover {
  background-color: #212121;
}

.custom-select::before {
  border-bottom: var(--size) solid #fff;
}

.custom-select::after {
  border-top: var(--size) solid #fff;
}

</style>