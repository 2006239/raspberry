import xml.etree.ElementTree as et
# import sys
jono = []
# filename = sys.argv[1]
# if filename is None:
filename = "testi33.txt"
tree = et.parse(filename)
root = tree.getroot()
laskuri = 0
for cycle in root.findall("cycle"):
    for gps in cycle.findall("gps"):
        lat = gps.find("lat").text
        lon = gps.find("lon").text
        jono.append("["+lon+","+lat+"]")
        if laskuri == 0:
            eka = "["+lat+","+lon+"]"
            laskuri+1

translation = {39: None}
merkkijono = str(jono)
file = open("html/script/ajoreitti.js", 'w')
file.write('var ajoreitti = {'+"\n")
file.write('    "type": "Feature",'+"\n")
file.write('    "geometry": {'+"\n")
file.write('        "type": "LineString",'+"\n")
file.write('        "coordinates":' + merkkijono.translate(translation)+"\n")
file.write('    },')
file.write('    "properties": {'+"\n")
file.write('        "name" : "ajoreitti"'+"\n")
file.write('     }'+"\n")
file.write('}'+"\n")
file.close()

file = open('html/script/aloitus.js', 'w')
file.write('var aloituspiste = '+eka+"\n")
file.close()
