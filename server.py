import socket, json, time, threading; 





class GameServer:

    def __init__(self, port_no):
        self.port_no = port_no;
        self.user_list = [];
    


    def start_server(self):

        self.sock = socket.socket(type=socket.SOCK_DGRAM);
        self.sock.bind(("", self.port_no));


        # Begin timer thread now

        while(True):
            msg, addr = self.sock.recvfrom(64000);
            size = int(msg.decode()[0:16]);
            payload = json.loads(msg.decode()[16:(16+size)]);

            # Probably check for proper formatting here or something


            if(payload["method"] == "connect"):
                print(payload["args"]["username"]);
                response = None;
                if(False):
                    # Do some authentication or something here! 

                    user_list.append({"username": payload["args"]["username"], "status": "loading", "address": addr});

                    response = {"method": "accept_connection", "args": None};
                else:
                    response = {"method": "reject_connection", "args": None};

                self.sock.sendto(f"{len(json.dumps(response)):>16}{json.dumps(response)}".encode(), addr);

            elif(payload["method"] == "initialized"):
                pass;

            elif(payload["method"] == "disconnect"):
                pass;

            elif(payload["method"] == "send_player_update"):
                pass;

            else:
                print("error", payload);

            













if __name__ == "__main__":
    crap = GameServer(6969);
    crap.start_server(); 