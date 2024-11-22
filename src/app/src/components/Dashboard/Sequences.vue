<script setup lang="ts">
    import { onMounted, Ref, ref } from 'vue';
    // SVGs
    import titleblockSVG from '../../../assets/titleblock.svg';
    // Thumbs
    import BoatPose from '../../../assets/guides/2_16_BoatPose.png';
    import UpwardSolute from '../../../assets/guides/1_02_UpwardSolute.png';
    import IntenseLegStretchPose from '../../../assets/guides/4_07_IntenseLegStretchPose.png';
    import EasyPoseVariationSideBend from '../../../assets/guides/3_07_EasyPoseVariationSideBend.png';
    

    const allHistory : Ref< Array<any> > = ref([]);
    const allSequences : Ref< Object > = ref({});
    const selectedSequence : Ref< number > = ref(-1);
    
    onMounted(async ()=>{
        allHistory.value = await window.landmarkerAPI.getAllHistory();
        console.log(allSequences);
    });

    function unselectAll() {
      let sequenceList = document.getElementById('sequence-list');
      if (sequenceList) {
        let sequenceElems = sequenceList.children;
        for (let i = 0; i < sequenceElems.length; i++) {
          const sequence = sequenceElems[i];
          sequence.className = "sequence-card";
        }
      }
    }

    function selectSequence(ev:Event) {
      let sequenceElement: HTMLElement = (<HTMLElement>ev.target);
      if (!sequenceElement ) return;

      // Select the parent 'Button' element instead of contents
      if (sequenceElement.parentElement instanceof HTMLButtonElement) {
        sequenceElement = sequenceElement.parentElement!;
      }
      else if (sequenceElement.parentElement?.parentElement instanceof HTMLButtonElement) {
        sequenceElement = sequenceElement.parentElement?.parentElement!;      
      } 
      if ( !(sequenceElement instanceof HTMLButtonElement) ) return;

      unselectAll();

      sequenceElement.className += " seq-selected";
      selectedSequence.value = parseInt(sequenceElement.getAttribute('sequenceId')!);

      // Get the sequence data via API
      console.log(selectedSequence.value);
      window.landmarkerAPI.getSequenceData(selectedSequence.value).then(
        (data)=>{
          console.log(data);
        }
      ).catch(
        (err)=>{ 
          console.log(err);
        }
      );
    }
</script>

<template>
    <div id="menu-seq-left">
        <div id="dash-header">
            <h1 id="header">Sequences</h1>
            <p class="colour-accent">Let's get started!</p>
        </div>
        <div id="sequence-list">
            <button class="sequence-card" sequenceId="1" sequence="general-fitness" @click="selectSequence">
                <img :src="UpwardSolute" alt="thumb" class="sequence-thumb">
                <div class="sequence-card-title">
                    <p class="colour-main">General Fitness Sequence (Sun Salutation A)</p>
                    <p class="colour-accent">Peak Pose</p>
                </div>
                <div class="proficiency-indicator" proficiency="beginner"></div>
            </button>
            <button class="sequence-card" sequenceId="2" sequence="core-strength"  @click="selectSequence">
                <img :src="IntenseLegStretchPose" alt="thumb" class="sequence-thumb">
                <div class="sequence-card-title">
                    <p class="colour-main">Core Strength Sequence</p>
                    <p class="colour-accent">Boat Pose</p>
                </div>
                <div class="proficiency-indicator" proficiency="beginner"></div>
            </button>
            <button class="sequence-card" sequenceId="3" sequence="weight-loss"  @click="selectSequence">
                <img :src="BoatPose" alt="thumb" class="sequence-thumb">
                <div class="sequence-card-title">
                    <p class="colour-main">Weight Loss Sequence</p>
                    <p class="colour-accent">Peak Pose</p>
                </div>
                <div class="proficiency-indicator" proficiency="intermediate"></div>
            </button>
            <button class="sequence-card" sequenceId="4" sequence="flexibility"  @click="selectSequence">
                <img :src="EasyPoseVariationSideBend" alt="thumb" class="sequence-thumb">
                <div class="sequence-card-title">
                    <p class="colour-main">Flexibility Sequence</p>
                    <p class="colour-accent">Easy Pose Variation Side Bend</p>
                </div>
                <div class="proficiency-indicator" proficiency="advanced"></div>
            </button>
        </div>
    </div>
    <hr>    
    <div id="menu-seq-info">
        <div id="info-header">
            <h3 id="info-header-title">Select a Pose Sequence</h3>
            <p id="info-header-posenum" class="colour-accent"></p>
            <div id="info-header-proficiency" class="proficiency-indicator" proficiency="beginner"></div>
        </div>
        <div id="info-recommendations">
            <div class="stat-title">
                <img :src="titleblockSVG">
                <p>Recommendations</p>
            </div>
            <p id="info-recommendations-text">Tag 1, Tag 2, Tag 3</p>
        </div>
        <div id="info-latest-best">
            <div id="latest-score">
                <p>Latest Score</p>
                <h3 id="info-latest-score">--</h3>
            </div>
            <div id="best-score">
                <p>Best Score</p>
                <h3 id="info-best-score">--</h3>
            </div>
        </div>
        <div id="info-scores">
            <div class="stat-title">
                <img :src="titleblockSVG">
                <p>Score Per Pose</p>
            </div>
            <div class="tableFixHead">
                  <table>
                    <thead>
                      <tr>
                        <th>Sequence Name</th>
                        <th>Score</th>
                      </tr>
                    </thead>
                    <tbody id="info-scores-table-body">
                    </tbody>
                </table>
            </div>
        </div>
        <button id="info-startbtn" onclick="_moveToSession()">Start</button>
    </div>
</template>

<style scoped>
.stat-title {
  display: flex;
  flex-direction: row;
  gap: 5px;
  width: 100%;
}

#sequence-list {
  display: flex;
  flex: 1;
  flex-wrap: wrap;
  gap: 10px;
  overflow-y: scroll;
}

.sequence-card {
  cursor: pointer;
  min-width: 200px;
  width: 200px;
  min-height: 200px;
  height: 300px;
  padding: 15px;
  border: 0px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  gap: 15px;
  background-color: var(--container-colour);
  box-shadow: #3333 0px 2px 15px;
  rotate: 0deg;
  transition: background-color 0.15s ease, rotate 0.5s ease, transform 0.1s ease;
  text-align: left;
  p {
    font-size: 14px;
  }
}
.sequence-card:hover {
  background: #3332;
}
.seq-selected {
  background-color: #1118;
  box-shadow: inset #ab9f8a55 0px 0px 10px;
  rotate: 2deg;
  transform: scale(0.95, 0.95);
}

.sequence-thumb {
  background-color: #0003;
  border-radius: 10px;
  width: -webkit-fill-available;
}

#menu-seq-info {
  width: 300px;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: center;
  transition: opacity 0.5s ease;
}

#info-header {
  display: flex;
  flex-direction: column;
  height: max-content;
  align-self: baseline;
  gap: 8px;
  h3 {
    margin: 0px;
  }
}

#info-recommendations {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

#info-latest-best {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  height: 100px;
  width: 100%;
  border-radius: 20px;
  background: linear-gradient(106deg,#4443 0%, #4441 100%);
  text-align: center;
  h3 {
    color: var(--main-colour);
    font-size: 40px;
    margin: 0px;
  }
}

#info-scores {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  thead {
    color: var(--accent-colour);
  }
}

#info-startbtn {
  width: 180px;
  border-radius: 10px;
  border: 0px;
  background-color: #171717;
  box-shadow: #8D8D8D12 0px 0px 10px;
  transition: background-color 0.3s linear;
  color: var(--main-colour);
  font-size: 15px;
  padding: 12px 40px;
  cursor: pointer;
  text-align: center;
}

#info-startbtn:hover {
  background-color: #1a1a1a;
}

</style>