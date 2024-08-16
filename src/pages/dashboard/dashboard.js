sessionStorage.setItem('userId', 0); 
// Include title bar and body via JQuery
let params = new URLSearchParams(location.search);
$(document).ready(()=>$('#app-title-bar').load('../../shared/apptitlebar.html'));
$("#main-content").ready(()=>{
    // Handle page parameter
    switch (params.get('page').toLowerCase()) {
        case 'dashboard':
            $('#main-content').load('contents/dashboard.html');
            break;
        case 'sequences':
            $('#main-content').load('contents/sequences.html');
            break;
        case 'scores':
            $('#main-content').load('contents/scores.html');
            break;
        case 'history':
            $('#main-content').load('contents/history.html');
            break;
    
        default:
            break;
    }
    updateNavBtns();
});

/**
 * Set the sequenceId to sessionStorage and move to session/index.html
 */
function moveToSession(sequenceId) {
    sessionStorage.setItem('sequenceId', sequenceId);
    location.href = "../session/index.html";
}


/**
 * Show the new contents depending on the page 
 */
function transitionTo(page) {
    params.set("page", page);
    updateNavBtns();
    
    const appContent = document.getElementById("main-content").style;
    appContent.animation = "opentransition 0.2s linear backwards";

    setTimeout(()=>{
        appContent.opacity = 0;
    }, 10);

    setTimeout(()=>{ 
        $("#main-content").html("");
        $('#main-content').load(`contents/${page}.html`);
        appContent.opacity = 1;
    }, 200);
}

// Highlight and disable the button of the current page 
function updateNavBtns() {
    let page = params.get("page");
    $('.sidenav-btn').attr('highlight', 'false');
    $(`#sidenav-btn-${page}`).attr('highlight', 'true');
}

// Function to draw the gauge
function drawGauge(canvas, ctx, percentage, colour) {
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
    
    ctx.font = 'bold 45px WorkSans';
    ctx.fillStyle = colour;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(percentage, canvas.width / 2, canvas.height / 2);
}