window.onload = () => {
    'use strict';
  
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
               .register('/sw.js');
    }
  }

var golink = function(divObj, apipath, afterFunction) {
    $(divObj).addClass("choosen");
    $.ajax(apipath).done(
        function(data) {
            if (afterFunction!==undefined) {
                afterFunction.call();
            }
        }
    );
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
    $.ajax("/api/temp").done(
	function(data) { //data is a json object of response 
	      $(".temp_line").text("Temperature in: "+data.temp_in+"*C out: "+data.temp_out+"*C "+"Humidity: "+data.humid+"%");
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
