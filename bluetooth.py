import bluetooth

def receiveMessages():
  server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
  addess =DC:FE:4D:6F:9C:F2 
  port = 20
  server_sock.bind(("",port))
  server_sock.listen(1)
  
  client_sock,address = server_sock.accept()
  print ("Yhteys muodostettu " + str(address))
  
  data = client_sock.recv(1024)
  print (": [%s]" % data)
  
  client_sock.close()
  server_sock.close()
  
def sendMessageTo(targetBluetoothMacAddress):
  port = 1
  sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
  sock.connect((targetBluetoothMacAddress, port))
  sock.send("hello!!")
  sock.close()
  
def lookUpNearbyBluetoothDevices():
  nearby_devices = bluetooth.discover_devices()
  for bdaddr in nearby_devices:
    print str(bluetooth.lookup_name( bdaddr )) + " [" + str(bdaddr) + "]"
    
    
lookUpNearbyBluetoothDevices()
