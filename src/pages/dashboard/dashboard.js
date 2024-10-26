sessionStorage.setItem('userId', 0); 
// Include title bar and body via JQuery
let params = new URLSearchParams(location.search);
$($('#app-title-bar').load('../../shared/apptitlebar.html'));
$(()=>{
    // Handle page parameter
    switch (params.get('page').toLowerCase()) {
        case 'dashboard':
            $('#main-content').load('contents/home.html');
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
})

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