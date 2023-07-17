var kaavio1,kaavio2,kaavio3,kaavio4;
var topraja = 100;
var alaraja = 0;
var ylaraja = 0;
var keskiarvonopeus = 0;
var korkeinnopeus = 0;
var keskikulutus = 0;
var korkeinkulutus = 0;
var polindefault = 0;
var raja = 0;
let file = document.getElementById("textfile");
let rivi;
var slider = document.getElementById("valitsin");
let arvo = slider.value;

var xml;
var cycle;


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



function parseXML(data)
{
	var parser = new DOMParser();
	//console.log(data.target.result);
	//document.write(data.target.result);
	this.xml = parser.parseFromString(data.target.result, "text/xml");
        this.cycle = this.xml.getElementsByTagName("cycle");
return this.xml;
}

function gpsdata(arvo)
{
    var sijainnit, lat, long, eka, vika;
    var edellinenlat = 0;
    var edellinenlong = 0;
    var latlong= [];
    var ajoreitti = [];
    var laskuri = 0;
    raja = cycle.length/topraja;
    alaraja = raja;
    var rajat = Math.round(raja*arvo);
    ylaraja = rajat;
    alaraja = Math.round(alaraja*(arvo-3)); 
    //if (ylaraja > 100) alaraja = 0;
    for(let i = 1; i<ylaraja;i++)
    {
        sijainnit = cycle[i].querySelector("gps");
        lat = sijainnit.querySelector("lat").textContent;
        long =  sijainnit.querySelector("lon").textContent;
        if(lat !=null && long !=null)
	{
		edellinenlat = lat;
		edellinenlong = long;
		latlong.push("["+long+","+lat+"]");
	}
        if(lat == null && long !=null)
	{
		lat = edellinenlat;
		latlong.push("["+long+","+lat+"]");
	}
        if(lat != null && long == null)
	{
		long = edellinenlong;
		latlong.push("["+long+","+lat+"]");
	}
        if(lat == null && long == null)
	{
		long = edellinenlong;
		lat = edellinenlat;
		latlong.push("["+long+","+lat+"]");
	}
        if (laskuri === 0)
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
/*
function accelerometer(arvo)
{
    var alku, x, y, rajaarvo;
    var luvut = [];
    var acc= [];
    var dataset = [];
    var suurimmat = [];
    var palautettava;
    var arvot = [];
    var acc = this.xml.getElementsByTagName("accelerometer");
    var rajaarvo = acc.length/topraja;
    rajaarvo = Math.round(rajaarvo*arvo);
    alku = rajaarvo - koko;
    for(let i = alku; i<rajaarvo;i++)
    {
        luvut = acc[i].getElementsByTagName("*");
        x = parseFloat(luvut[0].textContent);
        y = parseFloat(luvut[1].textContent);
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
    var merkkijono = JSON.stringify(dataset);
    //console.log(merkkijono.replace(/["]/g, ''));
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
  }]};

var config = {
  type: 'radar',
  scales: {
    myScale: {
      axis: 'r'
    }
  },
  data: data,
  options: {
	locale: "fi",
        maintainAspectRatio: false,
	
    elements: {
      line: {
        borderWidth: 3
      }
    }
  },
};


//console.log("TESTI: "+  JSON.stringify(data));
//palautettava = JSON.parse(data);
//console.log(data)
return config;
}
*/

function kaasupolin()
{
    var alku, highp, lowp;
    var edellinen = 0;
    var average = 0;
    high = 0;
    var pedal;
    var times;
    var gaspedal= [];
    var dataset = [];
    var timeset = [];
    var arvot = [];
    //rajaarvo = cycle.length/topraja;
    //rajaarvo = Math.round(rajaarvo*arvo);
    //alku = rajaarvo - this.raja;
    console.log(alaraja +" = "+ ylaraja);

    for(let i = alaraja; i<ylaraja;i++)
    {
	times = cycle[i].querySelector("time");
	if(times!=null)timeset.push(times.textContent);
	else{timeset.push("");}
    }
    
    for(let j = alaraja; j<ylaraja;j++)
    {
	pedal = cycle[j].querySelector("throttle_pos");
	if(pedal != null)
	{
		gaspedal = parseFloat(pedal.textContent.slice(0, -3));
		edellinen = gaspedal;
	}
	else gaspedal = edellinen;
	dataset.push(gaspedal);
	if (gaspedal > highp) highp = gaspedal;
	average = average + gaspedal;
    }
console.log(timeset.length.toString() + " = "+ dataset.length.toString());
//labels:timeset,
//datasets: [{
var data = {
    label: 'Kaasupolkimen asento',
    data: dataset,
    fill: true,
    borderColor: '#fff',
    tension: 0.1
};
/*
var config = {
  type: 'line',
  data: data,
  options: {
        maintainAspectRatio: false,
	
    elements: {
      line: {
        borderWidth: 3
      }
}}};
//console.log("nopeus: "+  JSON.stringify(config))
*/
return data;
}


function nopeus(arvo)
{
    var kaasu = kaasupolin();
    var kulut = kulutus();
    var alku, high, average, rajaarvo;
    var edellinen = 0;
    var average = 0;
    high = 0;
    var speed;
    var times;
    var nopeus= [];
    var dataset = [];
    var timeset = [];
    var arvot = [];
    rajaarvo = cycle.length/topraja;
    //rajaarvo = Math.round(rajaarvo*arvo);
    //alku = rajaarvo - this.raja;
    console.log(alaraja +" = "+ ylaraja);

    for(let i = alaraja; i<ylaraja;i++)
    {
	times = cycle[i].querySelector("time");
	if(times!=null)timeset.push(times.textContent);
	else{timeset.push("");}
    }
    
    for(let j = alaraja; j<ylaraja;j++)
    {
	speed = cycle[j].querySelector("speed");
	if(speed != null)
	{
		nopeus = parseInt(speed.textContent.slice(0, -3));
		edellinen = nopeus;
	}
	else nopeus = edellinen;
	dataset.push(nopeus);
	if (nopeus > high) high = nopeus;
	average = average + nopeus;
    }
console.log(timeset.length.toString() + " = "+ dataset.length.toString());

var data = {
	labels:timeset,
  datasets: [{
    label: 'Nopeus',
    data: dataset,
    fill: true,
    borderColor: '#fff',
    tension: 0.1
  },
	kaasu,
        kulut
	
]
};

var config = {
  type: 'line',
  data: data,
  options: {
        maintainAspectRatio: false,
	
    elements: {
      line: {
        borderWidth: 3
      }
}}};
//console.log("nopeus: "+  JSON.stringify(config))
return config;
}

function kulutus(arvo)
{
    var alku, highf;
    var edellinen = 0;
    var average = 0;
    high = 0;
    var fuel;
    var times;
    var fuelrate= [];
    var dataset = [];
    var timeset = [];
    var arvot = [];
    rajaarvo = cycle.length/topraja;
    //rajaarvo = Math.round(rajaarvo*arvo);
    //alku = rajaarvo - this.raja;
    console.log(alaraja +" = "+ ylaraja);

    for(let i = alaraja; i<ylaraja;i++)
    {
	times = cycle[i].querySelector("time");
	if(times!=null)timeset.push(times.textContent);
	else{timeset.push("");}
    }
    
    for(let j = alaraja; j<ylaraja;j++)
    {
	fuel = cycle[j].querySelector("fuel_rate");
	if(fuel != null)
	{
		fuelrate = parseFloat(fuel.textContent.slice(0, -3));
		edellinen = fuelrate;
	}
	else fuelrate = edellinen;
	dataset.push(fuelrate);
	if (fuelrate > highf) highf = fuelrate;
	average = average + fuelrate;
    }
console.log(timeset.length.toString() + " = "+ dataset.length.toString());
//	labels:timeset,
//  datasets: [{
var data = {
    label: 'Polttoaineenkulutus',
    data: dataset,
    fill: true,
    borderColor: '#fff',
    tension: 0.1
  };
/*
var config = {
  type: 'line',
  data: data,
  options: {
        maintainAspectRatio: false,
	
    elements: {
      line: {
        borderWidth: 3
      }
}}};
*/
//console.log("nopeus: "+  JSON.stringify(config))
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

function ReloadMap(arvo)
{
    //console.log(seuraa);
    let reitti = gpsdata(arvo);
    this.route.clearLayers();
    this.route = L.geoJSON(reitti[0]).addTo(this.map);
    if(document.getElementById("seuraa").checked) this.map.setView(reitti[2]);
//    kaavio1.destroy();
//    kaavio1 = new Chart(chart1, accelerometer(arvo));
    kaavio2.destroy();
    kaavio2 = new Chart(chart, nopeus(arvo));
    //kaavio3.destroy();
    //kaavio3 = new Chart(chart3, kulutus(raja));
}

var reader = new FileReader();
file.addEventListener("change", function () {
       reader.onload = function(data){
               parseXML(data);
               let reitti = gpsdata(arvo);
               kartta = DrawMap(reitti[1], reitti[0])
               //console.log(accelerometer(raja, arvo));
               //kaavio1 = new Chart(chart1, accelerometer(raja));
	       kaavio2 = new Chart(chart, nopeus(raja));
               //kaavio3 = new Chart(chart3, kulutus(raja));
       }
      reader.readAsText(this.files[0]);
      });

slider.oninput = function() {
	ReloadMap(this.value);
}








