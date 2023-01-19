let file = document.getElementById("textfile");
let rivi;
file.addEventListener("change", function () {
  let accel;
  let odb;
  let satellite;
  var parser = new DOMParser();
  var reader = new FileReader();
  reader.onload = function(data){
        // rivi = testi.toString().split(/\r\n|\n/);
        xml = parser.parseFromString(data.target.result, "application/xml");
        console.log(xml);
	//document.write(xml);
	}
   
  reader.readAsText(this.files[0]);

});