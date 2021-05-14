//Logic For Front End Alert Activation//

var t{{ al.alert_id }} = ({{ al.total }} * 1000)

$(document).ready( function() {

  function count{{ al.alert_id }}(change = 0) {
      t{{ al.alert_id }} = (t{{ al.alert_id }} - 1000);
      var t = t{{ al.alert_id }};
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
    var countDiv = document.getElementById('countdown{{ al.alert_id }}');

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
  var changing = count{{ al.alert_id }}().changes;

  count{{ al.alert_id }}(changing);  
  setInterval(count{{ al.alert_id }}, 1000);

});






$(document).ready(function(){
    $( "#toggle_rec{{ al.alert_id }}" ).change(function(event){
        console.log('Button is pressed!')
        if(this.checked) {
            $.get("/activate/{{ al.alert_id }}", function(data) {
                document.getElementById("datetime{{ al.alert_id }}").innerHTML = data;
                console.log("data then value:");
                console.log(data);
                console.log(data.value);
            });
            console.log("Toggle Button On is working");
            $( "#count_display{{ al.alert_id }}" ).show();
            $( "#count_display{{ al.alert_id }}" ).removeClass("hidden").addClass("col-6");
            $( "#countdown{{ al.alert_id }}").show();
            $( "#countdown{{ al.alert_id }}").removeClass("hidden").addClass("col-6");
            $( "#checked{{ al.alert_id }}").removeClass("hidden").addClass("visible").show();
            $( "#countdown{{ al.alert_id }}").css("display", "inline-block");
        }


        else {
            $.get("/deactivate/{{ al.alert_id }}");
            console.log("Toggle Button Off is working");
            $( "#count_display{{ al.alert_id }}" ).hide();
            $( "#countdown{{ al.alert_id }}").hide();
            $( "#checked{{ al.alert_id }}").hide()
        };
    
});
});