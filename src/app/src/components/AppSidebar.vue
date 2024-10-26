<script setup lang="ts">
    import pfpPNG from '../../assets/pfp.png' ;
</script>

<template>
    <section id="sidenav" class="container">
        <h1 id="logo">Yoge</h1>
        <div class="sidenav-spacer"></div>
        <div id="sidenav-btns">
            <button type="submit" class="sidenav-btn" id="sidenav-btn-dashboard">Home</button>
            <button type="submit" class="sidenav-btn" id="sidenav-btn-sequences">Sequences</button>
            <button type="submit" class="sidenav-btn" id="sidenav-btn-scores">Scores</button>
        </div>
        <div class="sidenav-spacer"></div>
        <div id="sidenav-bottom">
            <div id="sidenav-bottom-accountbtn">
                <img id="accountbtn-img" :src="pfpPNG" alt="">
                <p id="accountbtn-name">John Doe</p>
            </div>
            <!-- <hr> -->
            <!-- <div id="sidenav-bottom-btns"> -->
                <!-- <button type="submit" class="sidenav-btn" id="sidenav-btn-dashboard" onclick="transitionTo('dashboard')">Settings</button>
                <button type="submit" class="sidenav-btn" id="sidenav-btn-dashboard" onclick="transitionTo('dashboard')">About</button> -->
            <!-- </div> -->
        </div>
    </section>
</template>

<style scoped>
#sidenav {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  max-width: 200px;
  min-width: 160px;
  width: 160px;
}

#sidenav-btns{
  display: flex;
  flex-direction: column;
  gap: 10px;
}

#sidenav-bottom{
  display: flex;
  flex-direction: column;
  gap: 10px;

  hr {
    width: 100%;
  }
}

#sidenav-bottom-btns{
  display: flex;
  flex-direction: column;
  gap: 10px;
}

#sidenav-bottom-accountbtn {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0px 12px 0px 12px;
  gap: 10px;
}

.sidenav-spacer {
  flex-grow: 3;
}

.sidenav-btn {
  width: 100%;
	padding:12px 40px;

	background: transparent;
	display: inline-block;
	cursor: pointer;
	color: #ffffff;
	
	font-family: Arial;
	font-size:15px;
  text-align: left;
	text-shadow:0px 1px 0px #263666;
  
  border: 0px solid;
  border-radius: 10px;
  background: rgba(122,62,135,var(--bg-opacity));
  background: linear-gradient(90deg, rgba(122,62,135,var(--bg-opacity)) 6%, rgba(138,35,56,var(--bg-opacity)) 100%);
  box-shadow: inset 0px 0px 0px 0px #7a3e8700;
  transition: cubic-bezier(0, 0.8, 1, 1) box-shadow 1s;
}
.sidenav-btn:hover {
	box-shadow: inset 30px 0px 80px -50px #7a3e87dd;
}
.sidenav-btn:active {
	position:   relative;
  animation:  0.3s fadeIn 1 forwards;
  transition: linear box-shadow 0.08s;

  background: rgba(122, 62, 135, var(--bg-opacity));
  background: linear-gradient(90deg, rgba(122,62,135,var(--bg-opacity)) 6%, rgba(138,35,56,var(--bg-opacity)) 100%);
}
.sidenav-btn[highlight="true"] {
	position:   relative;
  font-weight: 700;

  animation:  0.3s fadeIn 1 forwards;
  transition: linear box-shadow 0.08s;
  
  background: rgba(122, 62, 135, var(--bg-opacity));
  background: linear-gradient(90deg, rgba(122,62,135,0.33) 6%, rgba(138,35,56,0.33) 100%);
  border: #333 1px solid 
}


#logo {
  font-size: 40px;
  margin: 10px auto 10px auto;
  text-align: center;
}
</style>