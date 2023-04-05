import socket, sys, json;


sock = socket.socket(type=socket.SOCK_DGRAM);
payload = {"method": sys.argv[1], "args": {"username": sys.argv[2]}};
msg = f"{len(json.dumps(payload)):>16}{json.dumps(payload)}";
sock.sendto(msg.encode(), ('localhost', 6969));
print(sock.recvfrom(64000)[0].decode());