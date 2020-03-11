import bluetooth
addr = 'ESP32test'
host = "24:6F:28:B5:1A:3A"
service_matches = bluetooth.find_service(address=host,name=b'ESP32SPP\x00')
first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.bind((addr,port))
sock.listen(10)
client_sock,address = sock.accept()
data = client_sock.recv(1024)
print('data')

client_sock.close()
sock.close()
