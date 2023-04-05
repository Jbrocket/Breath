import socket;




sock = socket.socket(type=socket.SOCK_DGRAM);
sock.bind(("localhost", 6969));




data, addr = sock.recvfrom(1024);
print(data);