//Logic For Front End Alert Activation//

var t{{ set.alert_set_id }} = ({{ set.total }} * 1000)

$(document).ready( function() {

  function count{{ set.alert_set_id }}(change = 0) {
      t{{ set.alert_set_id }} = (t{{ set.alert_set_id }} - 1000);
      var t = t{{ set.alert_set_id }};
      var seconds = Math.floor( (t/1000) % 60 );
      var minutes = Math.floor( (t/1000/60) % 60 );
      var hours = Math.floor( (t/(1000*60*60)) % 24 );
      var days = Math.floor( t/(1000*60*60*24) );


    if (seconds < 10) {
    // Add the "0" digit to the front
    // so 9 becomes "09"
    seconds = "0" + seconds;
    }

    if (minutes < 10) {
    // Add the "0" digit to the front
    // so 9 becomes "09"
    minutes = "0" + minutes;
    
    }

    // This gets a "handle" to the clock div in our HTML
    var countDiv = document.getElementById('countdown{{ set.alert_set_id }}');

    // Then we set the text inside the clock div 
    // to the hours, minutes, and seconds of the current time

    if(t > 0) {
    countDiv.innerText = days + " days & " + hours + ":" + minutes + ":" + seconds + " Remaining";
  
    return {
        'changes': change + 1 
    };
    }
    else {
    countDiv.innerText = "0 days and 0:00:00 Remaining";
  
    return {
        'changes': change 
    };

    }

  }

  // This runs the displayTime function the first time
  var changing = count{{ set.alert_set_id }}().changes;

  count{{ set.alert_set_id }}(changing);  
  setInterval(count{{ set.alert_set_id }}, 1000);

});






$(document).ready(function(){
    $( "#toggle_rec{{ set.alert_set_id }}" ).change(function(event){
        console.log('Button is pressed!')
        if(this.checked) {
            $.get("/activate/{{ set.alert_set_id }}", function(data) {
                document.getElementById("datetime{{ set.alert_set_id }}").innerHTML = data;
                console.log("data then value:");
                console.log(data);
                console.log(data.value);
            });
            console.log("Toggle Button On is working");
            $( "#count_display{{ set.alert_set_id }}" ).show();
            $( "#count_display{{ set.alert_set_id }}" ).removeClass("hidden").addClass("col-6");
            $( "#countdown{{ set.alert_set_id }}").show();
            $( "#countdown{{ set.alert_set_id }}").removeClass("hidden").addClass("col-6");
            $( "#checked{{ set.alert_set_id }}").removeClass("hidden").addClass("visible").show();
            $( "#countdown{{ set.alert_set_id }}").css("display", "inline-block");
        }


        else {
            $.get("/deactivate/{{ set.alert_set_id }}");
            console.log("Toggle Button Off is working");
            $( "#count_display{{ set.alert_set_id }}" ).hide();
            $( "#countdown{{ set.alert_set_id }}").hide();
            $( "#checked{{ set.alert_set_id }}").hide()
        };
    
});
});