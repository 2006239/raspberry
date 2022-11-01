##import bluetooth
import socket
def Connect():
    server_address = "DC:FE:4D:6F:9C:F2"
    server_port = 20
    backlog = 1
    size = 1024

    while True:
        with socket.socket(socket.AF_BLUETOOTH,
                           socket.SOCK_STREAM,
                           socket.BTPROTO_RFCOMM) as s:
            s.bind((server_address, server_port))
            s.listen(backlog)
            print('Odotetaan yhteytta...')
            client, address = s.accept()
            print(f'yhteys muodostettu: {address}')
            while True:
                try:
                    client.send(data)
                    data = client.recv(size)
                    if data:
                        print(data)
                        client.send(data)
                except ConnectionResetError:
                    print('Yhteys menetettiin')
                    break

"""                
def receiveMessages():
  server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
  address = "DC:FE:4D:6F:9C:F2"
  port = 20
  server_sock.bind((address,port))
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
"""