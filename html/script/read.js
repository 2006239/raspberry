let file = document.getElementById("textfile");
let rivi;
var slider = document.getElementById("valitsin");
let arvo = slider.value;


file.addEventListener("change", function () {
  
  let accel;
  let odb;
  var sijainnit;
  var lat, long, eka;
  var latlong= [];
  var eka;
  var laskuri = 0;
  var parser = new DOMParser();
  var reader = new FileReader();
  
reader.onload = function(data){
        xml = parser.parseFromString(data.target.result, "text/xml");
        
        var gps = xml.getElementsByTagName("gps");
	let raja = gps.length/100;
//document.write(raja);


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
       }

var merkkijono = latlong.toString();
var temp = '{"type": "Feature","geometry": {"type": "LineString","coordinates": [' +merkkijono+ ']},"properties": {"name" : "ajoreitti"}}';
var ajoreitti = JSON.parse(temp);

var kartta = document.getElementById("map");
const map = L.map(kartta).setView(eka, 12);
const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 19,
		attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
	}).addTo(map);
        L.geoJSON(ajoreitti).addTo(map);
	const marker = L.marker([51.5, -0.09]).addTo(map);


	}

reader.readAsText(this.files[0]);
});