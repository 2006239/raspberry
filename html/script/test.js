let file = document.getElementById("textfile");
let rivi;
var slider = document.getElementById("valitsin");
let arvo = slider.value;
var xml;
var eka;
var ajoreitti;
var map;
var kartta = document.getElementById("map");
var route;
function parseXML(data)
{
	var parser = new DOMParser();
	//console.log(data.target.result);
	//document.write(data.target.result);
	xml = parser.parseFromString(data.target.result, "text/xml");
return xml;
}

function gpsdata(arvo)
{
    var sijainnit, lat, long, eka, vika;
    var latlong= [];
    var ajoreitti = [];
    var laskuri = 0;
    var gps = xml.getElementsByTagName("gps");
    raja = gps.length/100;
    raja = Math.round(raja*arvo);
    for(let i = 1; i<raja;i++)
    {
        sijainnit = gps[i].getElementsByTagName("*");
        lat = sijainnit[0].textContent
        long =  sijainnit[1].textContent
        latlong.push("["+long+","+lat+"]");
        if (laskuri == 0)
        {
            eka = [lat, long];
            laskuri++;
        }
        vika = [lat, long];
    }
    var merkkijono = latlong.toString();
    var temp = '{"type": "Feature","geometry": {"type": "LineString","coordinates": [' +merkkijono+ ']},"properties": {"name" : "ajoreitti"}}';
    ajoreitti[0] = JSON.parse(temp);
    ajoreitti[1] = eka;
    ajoreitti[2] = vika;
return ajoreitti;
}
  
function DrawMap(eka, ajoreitti)
{
      //kartta = document.getElementById("map");
      this.map = L.map(kartta).setView(eka, 12);
const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 19,
		attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
	}).addTo(map);
    this.route = L.geoJSON(ajoreitti).addTo(map);
    //const marker = L.marker([51.5, -0.09]).addTo(map);
return map;
}

function ReloadMap(arvo)
{
    //console.log(seuraa);
    let reitti = gpsdata(arvo);
    this.route.clearLayers();
    this.route = L.geoJSON(reitti[0]).addTo(this.map);
    if(document.getElementById("seuraa").checked) this.map.setView(reitti[2]);
    //kartta = DrawMap(reitti[1], reitti[0]);
}

var reader = new FileReader();
file.addEventListener("change", function () {
       reader.onload = function(data){
               parseXML(data);
               let reitti = gpsdata(arvo);
               kartta = DrawMap(reitti[1], reitti[0])
       }
      reader.readAsText(this.files[0]);
      });

slider.oninput = function() {
	ReloadMap(this.value);
}








