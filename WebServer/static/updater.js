if (!!window.EventSource) {
    var fps_source = new EventSource("{{ url_for('fps_counter') }}");
    var bat_source = new EventSource("{{ url_for('battery_status') }}");
    var signal_source = new EventSource("{{ url_for('signal_status') }}");
    
    var infrared_source = new EventSource("{{ url_for('infrared_status') }}");
    var visible_source = new EventSource("{{ url_for('visible_status') }}");
    var controller_source = new EventSource("{{ url_for('controller_status') }}");
    
    fps_source.addEventListener('message', function(e) 
    {
        console.log("FPS:"+e.data);
        var m = document.getElementById("fps");
        m.innerHTML = e.data;
    }, false);
    
    bat_source.addEventListener('message', function(e)
    {
        console.log("Battery:"+e.data);
        var bat = document.getElementById("battery");
        bat.src = "../static/battery-"+e.data+".png";
    }, false);
    
    signal_source.addEventListener('message', function(e)
    {
        console.log("Signal:"+e.data);
        var bat = document.getElementById("signal");
        bat.src = "../static/signal-"+e.data+".png";
    }, false);
    
    infrared_source.addEventListener('message', function(e)
    {
        console.log("Infrared:"+e.data);
        var inf = document.getElementById("infrared");
        if(e.data == "ON") 
        {
            inf.src = "../static/light-infrared.png";
        }
        else
        {
            inf.src = "../static/clear.png";
        }
    }, false);
    
    visible_source.addEventListener('message', function(e)
    {
        console.log("Visible:"+e.data);
        var inf = document.getElementById("visible");
        if(e.data == "ON") 
        {
            inf.src = "../static/light-visible.png";
        }
        else
        {
            inf.src = "../static/clear.png";
        }
    }, false);
    
    controller_source.addEventListener('message', function(e)
    {
        console.log("Controller:"+e.data);
        var inf = document.getElementById("controller");
        if(e.data == "ON") 
        {
            inf.src = "../static/controller-on.png";
        }
        else if(e.data == "LOW") 
        {
            inf.src = "../static/controller-battery-crit.png";
        }
        else
        {
            inf.src = "../static/controller-off.png";
        }
    }, false);
}