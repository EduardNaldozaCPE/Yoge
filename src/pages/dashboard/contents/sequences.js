// Select the sequence card in URL parameters on load.
_updateSequenceCards();

// Include text for proficiency indicator.
$(".proficiency-indicator").each((i,e)=>{
    let proficiencyText = $(e).attr("proficiency");
    $(e).html(`<p>${proficiencyText.charAt(0).toUpperCase()}${proficiencyText.substring(1,proficiencyText.length)}</p>`);
});

// Show info of pre-selected sequence upon loading via sessionStorage.   
if (seqInfo !== undefined) var seqInfo;
seqInfo = JSON.parse( sessionStorage.getItem('sequence-info') );
if (seqInfo != null && seqInfo != "") { _updateInfoSection(seqInfo); }

// Handle getSequenceData callback.
landmarkerAPI.onSequenceData((_data)=>{ _updateInfoSection(_data) });


/** 
 * Update the "sequence" parameter, then calls _updateSequenceCards
*/
function updateSelect(elem) {
    params.set("sequence", $(elem).attr("sequence"));
    landmarkerAPI.getSequenceData($(elem).attr("sequenceId"));
    _updateSequenceCards();
}

/** 
 * Unselect the previously selected btn, and select the new one.
*/
function _updateSequenceCards() {
    if (selectedSequence === undefined) var selectedSequence;
    selectedSequence = params.get("sequence");
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

/**
 * Takes the necessary info from sessionStorage before running moveToSession() in dashboard/index.html 
 */
function _moveToSession() {
    let seqInfo = JSON.parse( sessionStorage.getItem('sequence-info') );;
    moveToSession( seqInfo['sequenceId'] );
}