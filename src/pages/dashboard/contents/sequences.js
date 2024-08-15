// Select the sequence card in URL parameters on load.
_updateSequenceCards();
if (selectedSequence === undefined) var selectedSequence;

// Include text for proficiency indicator.
$(".proficiency-indicator").each((i,e)=>{
    let proficiencyText = $(e).attr("proficiency");
    $(e).html(`<p>${proficiencyText.charAt(0).toUpperCase()}${proficiencyText.substring(1,proficiencyText.length)}</p>`);
});

// Show info of pre-selected sequence upon loading via sessionStorage.   
if (seqInfo !== undefined) var seqInfo;
seqInfo = JSON.parse( sessionStorage.getItem('sequence-info') );
if (seqInfo != null && seqInfo != "") {
    _updateInfoSection(seqInfo);
    landmarkerAPI.getHistory(parseInt(seqInfo.sequenceId));
    landmarkerAPI.getPoseRecords(parseInt(seqInfo.sequenceId));
}

// Handle getSequenceData callback.
landmarkerAPI.onSequenceData((_data)=>{ 
    _updateInfoSection(_data)
    landmarkerAPI.getHistory(parseInt(_data.sequenceId));
    landmarkerAPI.getPoseRecords(parseInt(_data.sequenceId));
});


/** 
 * Update the "sequence" parameter, then calls _updateSequenceCards
*/
function updateSelect(elem) {
    params.set("sequence", $(elem).attr("sequence"));
    selectedSequence = params.get("sequence");
    landmarkerAPI.getSequenceData($(elem).attr("sequenceId"));
    _updateSequenceCards();
}

/** 
 * Unselect the previously selected btn, and select the new one.
*/
function _updateSequenceCards() {
    $(".sequence-card").each((i, e)=>{
        if (selectedSequence != $(e).attr("sequence")) {
            $(e).removeAttr("select");
        } else {
            $(e).attr("select", "true");
        }
    });
}

/**
 *  When data is ready, update the info section to show the sequence info. 
 */
function _updateInfoSection(data) {
    sessionStorage.setItem('sequence-info', JSON.stringify(data));
    $("#menu-seq-info").css('opacity', 1);
    $("#info-header-title").text(data.sequenceName);
    $("#info-header-posenum").text(`${data.sequenceName} Poses`);
    $("#info-header-proficiency")
        .attr("proficiency", data.difficulty.toLowerCase())
        .text(data.difficulty)
        .attr("hidden", false);
    $("info-recommendations-text").text(data.tags);
}

landmarkerAPI.onHistory((data)=>{
    let bestScore   = 0;
    let latestScore = 0;
    if (data.length != 0) {
        for (let i = 0; i < data.length; i++) {
            if (data[i].score > bestScore)
                bestScore = data[i].score;
            if (i == data.length-1)
                latestScore = data[i].score;
        }
    }
    $("#info-latest-score").text(latestScore.toFixed(2));
    $("#info-best-score").text(bestScore.toFixed(2));
})
landmarkerAPI.onPoseRecords((data)=>{
    let newTable = $("#info-scores-table-body").html("");
    for (let i = 0; i < data.length; i++) {
        newTable = newTable.add(`<tr>
            <td>${data[i].poseName}</td>
            <td>${data[i].bestScore.toFixed(2)}</td>
        </tr>`);
    }
    $("#info-scores-table-body").html(newTable);
})

/**
 * Takes the necessary info from sessionStorage before running moveToSession() in dashboard/index.html 
 */
function _moveToSession() {
    let seqInfo = JSON.parse( sessionStorage.getItem('sequence-info') );;
    moveToSession( seqInfo['sequenceId'] );
}