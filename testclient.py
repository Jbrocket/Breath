import socket, sys, json;


sock = socket.socket(type=socket.SOCK_DGRAM);
sock.settimeout(1);
sock.bind(("", 4243));
payload = {"method": sys.argv[1], "args": {"username": sys.argv[2]}};
msg = f"{len(json.dumps(payload)):>16}{json.dumps(payload)}";
sock.sendto(msg.encode(), ('localhost', 6969));
print(sock.recvfrom(64000)[0].decode());

payload = {"method": "send_player_update", "args" : {"username": sys.argv[2], "input": "up"}};
msg = f"{len(json.dumps(payload)):>16}{json.dumps(payload)}";
sock.sendto(msg.encode(), ('localhost', 6969));
print(sock.recvfrom(64000)[0].decode());

payload = {"method": "send_player_update", "args" : {"username": sys.argv[2], "input": "left"}};
msg = f"{len(json.dumps(payload)):>16}{json.dumps(payload)}";
sock.sendto(msg.encode(), ('localhost', 6969));
print(sock.recvfrom(64000)[0].decode());
payload = {"method": "send_player_update", "args" : {"username": sys.argv[2], "input": "down"}};
msg = f"{len(json.dumps(payload)):>16}{json.dumps(payload)}";
sock.sendto(msg.encode(), ('localhost', 6969));
print(sock.recvfrom(64000)[0].decode());
