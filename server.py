import socket, json, time, threading, collections;
from src import megalib

class GameServer:

    def __init__(self, port_no):
        self.port_no = port_no;
        self.user_list = collections.defaultdict(lambda: None);
        self.buffer = {"players": {}, "tanks": {}}
        self.map_x = 4950; # /50 = 99
        self.map_y = 2880; # /48 = 60
        self.map_x_offset = -470;
        self.map_y_offset = -325;
        #self.tank_list = megalib.O2Tanks();
        #self.tank_list.create_tanks(10);
        tankies = megalib.O2Tanks()
        tankies.create_tanks(10);
        self.tank_list = {};
        for i in range(10):
            self.tank_list[i] = {"x": tankies.O2_tanks[i].x, "y": tankies.O2_tanks[i].y};

    

    def update_players(self):
        while True:
            user: megalib.Player
            if self.buffer["players"] or self.buffer["tanks"]:
                for user in self.user_list:
                    self.sock.sendto(f"{json.dumps(self.buffer)}".encode(), self.user_list[user].ip_address)
                    pass
                self.buffer = {"players": {}, "tanks": {}}
            time.sleep(0.0083)
        
        return

    def start_server(self):

        host_name = socket.gethostname()
        ip_address = socket.gethostbyname(host_name)
        self.sock = socket.socket(type=socket.SOCK_DGRAM);
        self.sock.bind((ip_address, self.port_no));
        print(f"Listening on port {self.sock.getsockname()[1]}, on address {ip_address}")


        # Begin timer thread now
        t = threading.Thread(target=self.update_players, daemon=True)
        t.start()
        
        while(True):
            msg, addr = self.sock.recvfrom(64000);
            size = int(msg.decode()[0:16]);
            payload = json.loads(msg.decode()[16:(16+size)]);

            # Probably check for proper formatting here or something


            if(payload["method"] == "connect"):
                response = None;
                if(not self.user_list[payload["args"]["username"]]):
                    # Do some authentication or something here! 
                    new_user = megalib.Player(payload["args"]["username"])
                    new_user.last_heard_from = time.time()
                    new_user.x = 2255
                    new_user.y = 365
                    new_user.status = "loaded"
                    new_user.ip_address = addr
                    response = {"status": "accept", "players": {}, "tanks": {}}

                    for user in self.user_list:
                        if not self.user_list[user]:
                            continue
                        response['players'][user] = {"status": self.user_list[user].status, "x": self.user_list[user].x, "y": self.user_list[user].y}
                    for i in range(len(self.tank_list)):
                        #response['tanks'][i] = {"x": self.tank_list.O2_tanks[i].x * 50 + self.map_x_offset, "y": self.tank_list.O2_tanks[i].y * 48 + self.map_y_offset};
                        response['tanks'][i] = {"x": self.tank_list[i]['x']*50 + self.map_x_offset, "y":self.tank_list[i]['y']*48 + self.map_y_offset};
                    self.user_list[new_user.name] = new_user

                    #response = {"method": "accept_connection", "args": None};
                    response['players'][new_user.name] = {"status": "accept", "x": new_user.x, "y": new_user.y}
                    response["status"] = "accept"
                    print(response);
                    self.buffer['players'][new_user.name] = {"x": new_user.x, "y": new_user.y}
                    
                else:
                    response = {"status": "reject", "args": {"reason": "duplicate name"}};

                self.sock.sendto(f"{len(json.dumps(response)):>16}{json.dumps(response)}".encode(), addr);

            elif(payload["method"] == "initialized"):
                pass;

            elif(payload["method"] == "disconnect"):
                pass;

            elif(payload["method"] == "send_player_update"):
                self.update_player_position(payload["args"]);

                # response = {payload["args"]["username"]: {"x": self.user_list[payload["args"]["username"]].x, "y": self.user_list[payload["args"]["username"]].y}};

                # self.sock.sendto(json.dumps(response).encode(), addr);

            else:
                print("error", payload);
            




    def update_player_position(self, args):
        username = args["username"];
        self.user_list[username].x = args["x"]
        self.user_list[username].y = args["y"]
        #print(args['x'], args['y']);
        #print(self.tank_list.O2_tanks[0].x*50+self.map_x_offset, self.tank_list.O2_tanks[0].y*48 +self.map_y_offset);
        # Check here for
        for tank in self.tank_list:
            if(args["x"] > (self.tank_list[tank]['x']*50+self.map_x_offset-50) and args["x"] < (self.tank_list[tank]['x']*50+self.map_x_offset + 100) and args["y"] > (self.tank_list[tank]['y']*48+self.map_y_offset-75) and args["y"] <(self.tank_list[tank]['y']*48+self.map_y_offset + 75)):
                self.buffer['tanks'][tank] = {"method": "delete"};
                print('got me');
                self.tank_list.pop(tank); 
                #print("OP!!", tank, self.tank_list.pop(tank));
                break;
            #print(tank);
        self.buffer["players"][username] =  {"x": self.user_list[username].x, "y": self.user_list[username].y}










if __name__ == "__main__":
    server = GameServer(6969);
    server.start_server(); 