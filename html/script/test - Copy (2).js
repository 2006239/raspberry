var raja = 0;
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
var chart1 = document.getElementById('chart1');
    var highx = 0;
    var highy = 0;
    var lowx = 0;
    var lowy = 0;


  //new Chart(chart1, accelerometer(koko, arvo));

function parseXML(data)
{
	var parser = new DOMParser();
	//console.log(data.target.result);
	//document.write(data.target.result);
	this.xml = parser.parseFromString(data.target.result, "text/xml");
return this.xml;
}

function gpsdata(arvo)
{
    var sijainnit, lat, long, eka, vika;
    var latlong= [];
    var ajoreitti = [];
    var laskuri = 0;
    var gps = this.xml.getElementsByTagName("gps");
    raja = gps.length/100;
    this.raja = raja;
    raja = Math.round(raja*arvo);
    for(let i = 1; i<raja;i++)
    {
        sijainnit = gps[i].getElementsByTagName("*");
        lat = sijainnit[0].textContent;
        long =  sijainnit[1].textContent;
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

function accelerometer(koko, arvo)
{
    var alku, x, y, rajaarvo;
    var luvut = [];
    var acc= [];
    var dataset = [];
    var suurimmat = [];
    var palautettava;
    var arvot = [];

    var acc = this.xml.getElementsByTagName("accelerometer");
    rajaarvo = acc.length/100;
    rajaarvo = Math.round(rajaarvo*arvo);
    alku = rajaarvo - koko;
    console.log(alku);
    for(let i = alku; i<rajaarvo;i++)
    {
        luvut = acc[i].getElementsByTagName("*");
        x = Number(luvut[0].textContent);
        y = Number(luvut[1].textContent);
        dataset.push({ x: x, y: y});
        if (y < 0) if(y<this.lowy) lowy = y;
	if (x < 0) if(x<this.lowx) lowx = x;
        if (y > 0) if(y >this.highy) highy = y;
	if (x > 0) if(x >this.highx) highx = y;
        suurimmat[0]= this.lowy;
        suurimmat[1]= this.lowx;
        suurimmat[2]= this.highy;
        suurimmat[3]= this.highx;
    }
    //var merkkijono = dataset.toString();
    //console.log(merkkijono);
//    let temp = JSON.parse(merkkijono);
//    palautettava[0] = merkkijono;
//    palautettava[1] = suurimmat;

var data = {
  labels: [
    'X',
    'Y',
    '-X',
    '-Y'
  ],
  datasets: [{
    label: 'G-voimat',
    data: dataset,
    fill: true,
    backgroundColor: 'rgba(255, 99, 132, 0.2)',
    borderColor: 'rgb(255, 99, 132)',
    pointBackgroundColor: 'rgb(255, 99, 132)',
    pointBorderColor: '#fff',
    pointHoverBackgroundColor: '#fff',
    pointHoverBorderColor: 'rgb(255, 99, 132)'
  }, {
    label: 'My Second Dataset',
    data: [28, 48, 40, 19, 96, 27, 100],
    fill: true,
    backgroundColor: 'rgba(54, 162, 235, 0.2)',
    borderColor: 'rgb(54, 162, 235)',
    pointBackgroundColor: 'rgb(54, 162, 235)',
    pointBorderColor: '#fff',
    pointHoverBackgroundColor: '#fff',
    pointHoverBorderColor: 'rgb(54, 162, 235)'
  }]
};



console.log("TESTI: "+  JSON.stringify(data));
//palautettava = JSON.parse(data);
//console.log(data)
return data;
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

function ReloadMap(arvo, rajaarvo)
{
    //console.log(seuraa);
    let reitti = gpsdata(arvo);
    this.route.clearLayers();
    this.route = L.geoJSON(reitti[0]).addTo(this.map);
    if(document.getElementById("seuraa").checked) this.map.setView(reitti[2]);
    new Chart(chart1, accelerometer(rajaarvo, arvo));
}

var reader = new FileReader();
file.addEventListener("change", function () {
       reader.onload = function(data){
               parseXML(data);
               let reitti = gpsdata(arvo);
               kartta = DrawMap(reitti[1], reitti[0])
               new Chart(chart1, accelerometer(raja, arvo));
       }
      reader.readAsText(this.files[0]);
      });

slider.oninput = function() {
	ReloadMap(this.value, raja);
}








