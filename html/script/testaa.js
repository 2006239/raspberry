var kaavio;
var aloitusluku = 30;
var sijainti = 0;
var updatearvo = 600;
var paivitysarvo = 1;
var updateraja = 30;
var updatealaraja = 0;
var updateylaraja = 0;
var alaraja = 0;
var ylaraja = 0;
var keskiarvonopeus = 0;
var korkeinnopeus = 0;
var keskikulutus = 0;
var korkeinkulutus = 0;
var merenpinnasta = 1361.5;
var korkeinkohta = 0;
var polindefault = 0;
var vanhaarvo = aloitusluku;
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

function parsekorkeus(data) {
    var sijainnit;
    var korkeus;
    for (let i = 0; i < data.length; i++) {
        sijainnit = data[i].querySelector("gps");
        temp = sijainnit.querySelector("altitude");
        if (temp != null) {
            korkeus = parseFloat(temp.textContent);
            if (korkeus < merenpinnasta) { merenpinnasta = korkeus; }
            if (korkeinkohta < korkeus) { korkeinkohta = korkeus; }
        }
    }
	return true;
}

function parseXML(data) {
  var parser = new DOMParser();
  this.xml = parser.parseFromString(data.target.result, "text/xml");
  this.cycle = this.xml.getElementsByTagName("cycle");
  slider.setAttribute("max", this.cycle.length/paivitysarvo);
  slider.setAttribute("value", aloitusluku);
  parsekorkeus(this.cycle);
  return this.xml;
}


function gps(merkkijono) {
    var luku = parseInt(merkkijono, 10) - 2;

    var sijainnit, lat, long, eka, vika, korkeus;
    var edellinenlat = 0;
    var edellinenlong = 0;
    var latlong = [];
    var ajoreitti = [];
    var laskuri = 0;
    updateylaraja = updateraja;
    if (luku < cycle.length - 1) {
        if (luku < aloitusluku) {

            updatealaraja = 0;
            updateylaraja = aloitusluku;
        }
        else {
            updateylaraja = luku;
            updatealaraja = updateylaraja - updateraja;
            if (luku > (vanhaarvo + 5) || luku < vanhaarvo) {
                if (luku > aloitusluku) {
                    updateylaraja = luku;
                    updatealaraja = updateylaraja - aloitusluku;
                }
                else {
                    updataalaraja = 0;
                    updateylaraja = aloitusluku;
                }
            }
        }
    }
    else {
        updateylaraja = cycle.lenght; updatealaraja = cycle.length - aloitusluku;
    }
    vanhaarvo = luku;
    //console.log(cycle.length);
    for (let i = 0; i < updateylaraja; i++) {
        sijainnit = cycle[i].querySelector("gps");
        lat = sijainnit.querySelector("lat").textContent;
        long = sijainnit.querySelector("lon").textContent;
        if (lat != null && long != null) {
            edellinenlat = lat;
            edellinenlong = long;
            latlong.push("[" + long + "," + lat + "]");
        }
        if (lat == null && long != null) {
            lat = edellinenlat;
            latlong.push("[" + long + "," + lat + "]");
        }
        if (lat != null && long == null) {
            long = edellinenlong;
            latlong.push("[" + long + "," + lat + "]");
        }
        if (lat == null && long == null) {
            long = edellinenlong;
            lat = edellinenlat;
            latlong.push("[" + long + "," + lat + "]");
        }
        if (laskuri === 0) {
            eka = [lat, long];
            laskuri++;
        }
        vika = [lat, long];
    }

    var merkkijono = latlong.toString();

    var temp = '{"type": "Feature","geometry": {"type":  "LineString","coordinates": [' + merkkijono + ']},"properties":   {"name" : "ajoreitti"}}';

    ajoreitti[0] = JSON.parse(temp);
    ajoreitti[1] = eka;
    ajoreitti[2] = vika;

    return ajoreitti;
}

function accelerometer() {
    var x,y,z,sijainnit;
    var dataset = [];
    var gvoima = 0;
    edellinen = 0;

    for (let j = updatealaraja; j < updateylaraja; j++) {
        sijainnit = cycle[j].querySelector("accelerometer");
	    if(sijainnit !=null){
           x = sijainnit.querySelector("x");
    	   y = sijainnit.querySelector("y");
           z = sijainnit.querySelector("z");
        }

        if (z != null && y != null && x !=null) {
 
            gvoima = Math.sqrt(Math.pow(parseFloat(x.textContent),2) + Math.pow(parseFloat(y.textContent),2) +Math.pow(parseFloat(z.textContent),2));
 	        edellinen = gvoima;
            console.log(gvoima);
        }
        else
        {gvoima = edellinen;}
        dataset.push(gvoima);
    }
    return dataset;
}


function korkeus() {
    var sijainnit, edellinenkorkeus, korkeus;
    var altitude = [];
    for (let j = updatealaraja; j < updateylaraja; j++) {
        sijainnit = cycle[j].querySelector("gps");
        korkeus = sijainnit.querySelector("altitude");
        if (korkeus != null) {
            edellinenkorkeus = korkeus.textContent;
            altitude.push(parseFloat(korkeus.textContent)); //-merenpinnasta);
        }
        if (korkeus == null) {
            korkeus = edellinenkorkeus;
            //if(korkeus !=0){altitude.push(parseFloat(korkeus));}//-merenpinnasta);}
            altitude.push(parseFloat(korkeus));
        }
    }
    return altitude;
}



function gpsnopeus() {
    var edellinen = 0;
    var speed, sijainnit;
    var nopeus;
    var dataset = [];
    for (let j = updatealaraja; j < updateylaraja; j++) {
        sijainnit = cycle[j].querySelector("gps");
        speed = sijainnit.querySelector("speed");
        if (speed != null) {
            nopeus = parseInt(speed.textContent);
            edellinen = nopeus;
        }
        else nopeus = edellinen;
        dataset.push(nopeus);
    }
    return dataset;
}


/*
function nopeus() {
    var edellinen = 0;
    var speed;
    var nopeus;
    var dataset = [];
    var laskuri = 0;
    for (let j = updatealaraja; j < updateylaraja; j++) {
        speed = cycle[j].querySelector("speed");
        if (speed != null) {
            nopeus = parseInt(speed.textContent);
            edellinen = nopeus;
        }
        else nopeus = edellinen;
        dataset.push(nopeus);
        laskuri++
        if (laskuri > 30) {
            return false;
        }
    }
    return dataset;
}

function rpm() {
    var edellinen = 0;
    var revs;
    var kierrosluku = [];
    var dataset = [];
    for (let j = updatealaraja; j < updateylaraja; j++) {
        revs = cycle[j].querySelector("rpm");
        if (revs != null) {
            kierrosluku = parseFloat(revs.textContent);
            edellinen = kierrosluku;
        }
        else {
            kierrosluku = edellinen;
        }
        dataset.push(kierrosluku);
    }
    return dataset;
}

function kulutus() {
    var edellinen = 0;
    var fuel;
    var fuelrate = [];
    var dataset = [];
    for (let j = updatealaraja; j < updateylaraja; j++) {
        fuel = cycle[j].querySelector("fuel_rate");
        if (fuel != null) {
            fuelrate = parseFloat(fuel.textContent);
            edellinen = fuelrate;
        }
        else fuelrate = edellinen;
        dataset.push(fuelrate);
    }
    return dataset;
}

function jarrut() {
    var edellinen = 0;
    var brakes;
    var brake = [];
    var dataset = [];
    for (let j = updatealaraja; j < updateylaraja; j++) {
        brake = cycle[j].querySelector("brake");
        if (brake != null) {
            brakes = parseFloat(brake.textContent);
            edellinen = brakes;
        }
        else brakes = edellinen;
        dataset.push(brakes);
    }
    return dataset;
}
*/
//chart format
function drawChart(arvo) {
    //var kierrosluvut = rpm();
    //var kulut = kulutus();
    var altitude = korkeus();
    var gforce = accelerometer();
    //if (nopeus()) { var speed = nopeus; }
    var speed = gpsnopeus();
    //var brake = jarrut();
    var times;
    var timeset = [];
    for (let i = 0; i < updateylaraja; i++) {
        times = cycle[i].querySelector("time");
        if (times != null) timeset.push(times.textContent.slice(11));
        else { timeset.push(""); }
    }

    var data = {
        labels: timeset,
        datasets: [{
            label: 'Nopeus',
            data: speed,
            borderColor: 'rgb(0, 255, 0)',
            backgroundColor: 'rgba(0, 255, 0, 0.5)',
            tension: 0.1,
            yAxisID: 'y1',
            order: 1
        },
        /*{
            label: 'Kierrosluku',
            data: kierrosluvut,
            borderColor: 'rgb(255, 0, 0)',
            backgroundColor: 'rgba(255, 0, 0, 0.5)',
            tension: 0.1,
            yAxisID: 'y',
            order: 2
        },
        {
            label: 'Polttoaineenkulutus',
            data: kulut,
            borderColor: 'rgb(0, 0, 255)',
            backgroundColor: 'rgba(0, 0, 255, 0.5)',
            tension: 0.1,
            yAxisID: 'y',
            order: 1
        },*/
        {
            label: 'Kiihtyvyys',
            data: gforce,
            borderColor: 'rgb(255, 0, 255)',
            backgroundColor: 'rgba(255, 0, 255, 0.5)',
            tension: 0.1,
            yAxisID: 'y',
            order: 3
        },/*
        {
            label: 'Jarrutus',
            data: brake,
            fill: true,
            borderColor: 'rgb(255, 255, 0)',
            backgroundColor: 'rgba(255, 255, 0, 0.5)',
            tension: 0.1,
            yAxisID: 'y',
            order: 4
        },*/
        {
            label: 'Korkeus',
            size: 20,
            data: altitude,
            fill: true,
            borderColor: 'rgb(160, 160, 160)',
            backgroundColor: 'rgba(160, 160, 160, 0.5)',
            tension: 0.1,
            yAxisID: 'y1',
            order: 2
        }

        ]
    };
    var config = {
        type: 'line',
        data: data,
        options: {
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    min: 0,
                    position: 'left',
                },
                y1: {
                    beginAtZero: true,
                    min: merenpinnasta,
                    max: korkeinkohta,
                    position: 'right',
                    // grid line settings
                    grid: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    }
                }
            },
            /*plugins: {
              title: {
                display: true,
                text: 'Testi',
                font: {
                  size: 30
                }
              }
            },*/
            elements: {
                line: {
                    borderWidth: 3
                }
            }
        }
    };
    return config;
}

//gather chart data
function updateChart() {
    //var kierrosluvut = rpm();
    //var consumption = kulutus();
    var speed = gpsnopeus();
    var altitude = korkeus();
    var gforce = accelerometer();
    //var brake = jarrut();
    const data = [];
    var times;
    var timeset = [];
    for (let i = updatealaraja; i < updateylaraja; i++) {
        times = cycle[i].querySelector("time");
        if (times != null) timeset.push(times.textContent.slice(11));
        else { timeset.push(""); }
    }
    data[0] = timeset;
    data[1] = speed;
    //data[2] = kierrosluvut;
    //data[3] = consumption;
    data[2] = gforce;
    //data[5] = brake;
    data[3] = altitude;

    return data;
}
//redraw chart data
function KaavioUpdate(data, chart) {
    chart.data.labels = data[0];
    chart.data.datasets[0].data = data[1];
    chart.data.datasets[1].data = data[2];
    chart.data.datasets[2].data = data[3];
    //chart.data.datasets[3].data = data[4];
    //chart.data.datasets[4].data = data[5];
    //chart.data.datasets[5].data = data[6];
    chart.update("none");

}
//openstreetmap
function DrawMap(eka, ajoreitti) {
    this.map = L.map(kartta).setView(eka, 12);
    const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    this.route = L.geoJSON(ajoreitti[0]).addTo(map);

    return map;
}

//slider movement to update page content
function UpdatePage(slideri) {
    let reitti = gps(slideri);
    this.route.clearLayers();
    this.route = L.geoJSON(reitti[0]).addTo(this.map);
    this.map.setView(reitti[2]);
    KaavioUpdate(updateChart(slideri), kaavio);
}

var reader = new FileReader();
file.addEventListener("change", function () {
  reader.onload = function (data) {
    parseXML(data);
    let reitti = gps(arvo);
    kartta = DrawMap(reitti[1], reitti[0])
    kaavio = new Chart(chart, drawChart(raja));
  }
  reader.readAsText(this.files[0]);
});








