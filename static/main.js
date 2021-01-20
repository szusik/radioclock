window.onload = () => {
    'use strict';
  
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
               .register('/static/sw.js');
    }
  }

var golink = function(divObj, apipath) {
    $(divObj).addClass("choosen");
    $.ajax(apipath);
    setTimeout(function(){
        $(divObj).removeClass("choosen");
    },1000);               
}

function updateVolume(){
    $.ajax("/api/volume/level").done(
        function(data) { //data is a json object of StatusAnswer object response 
            $(".volume_line").text("Current volume: " +data.status);
        }
    );
}

$.ajaxSetup({
    async: false
});
$(document).ajaxComplete(function( event, xhr, settings ) {
    
        $( ".state_line" ).text( settings.url+" : " + xhr.status + " - "+ xhr.statusText );
    
})
$(document).ajaxSend(function( event, xhr, settings ) {
    
    $( ".state_line" ).text( "Calling " + settings.url+" ... ");

})
$(document).ready(updateVolume())