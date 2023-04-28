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
    
    # def new_tanks(self):
    #     while True:
    #         for tank in self.tank_list:
    #             self.buffer['tanks'][tank] = {"method": "delete"};
    #         self.tank_list = {}
    #         tankies = megalib.O2Tanks()
            
    #         num: int
    #         num = 50
    #         tankies.create_tanks(num);
    #         for i in range(num):
    #             self.tank_list[i] = {"x": tankies.O2_tanks[i].x, "y": tankies.O2_tanks[i].y};
    #         for tank in self.tank_list:
    #             self.buffer['tanks'][tank]{"x": self.tank_list[tank]['x']*50 + self.map_x_offset, "y":self.tank_list[tank]['y']*48 + self.map_y_offset}
    #         time.sleep(10)
    
    def lower_oxygen(self):
        while True:
            
            for username in self.user_list:
                self.user_list[username].O2_level = self.user_list[username].O2_level - 5 if self.user_list[username].O2_level - 5 > 0 else 0
                if self.user_list[username].O2_level == 0:
                    self.user_list[username].dead = True
                    self.user_list[username].death_counter += 1
                self.buffer["players"][username] = {"x": self.user_list[username].x, "y": self.user_list[username].y, "O2": self.user_list[username].O2_level, "score": self.user_list[username].death_counter, "dead": self.user_list[username].dead}
            
            time.sleep(1)

    def start_server(self):

        host_name = socket.gethostname()
        ip_address = socket.gethostbyname(host_name)
        self.sock = socket.socket(type=socket.SOCK_DGRAM);
        self.sock.bind((ip_address, self.port_no));
        print(f"Listening on port {self.sock.getsockname()[1]}, on address {ip_address}")


        # Begin timer thread now
        t = threading.Thread(target=self.update_players, daemon=True)
        p = threading.Thread(target=self.lower_oxygen, daemon=True)
        # c = threading.Thread(target=self.new_tanks, daemon=True)
        # c.start()
        p.start()
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
                        response['players'][user] = {"status": self.user_list[user].status, "x": self.user_list[user].x, "y": self.user_list[user].y, "dead": self.user_list[user].dead }
                    for tank in self.tank_list:
                        #response['tanks'][i] = {"x": self.tank_list.O2_tanks[i].x * 50 + self.map_x_offset, "y": self.tank_list.O2_tanks[i].y * 48 + self.map_y_offset};
                        response['tanks'][tank] = {"x": self.tank_list[tank]['x']*50 + self.map_x_offset, "y":self.tank_list[tank]['y']*48 + self.map_y_offset};
                    self.user_list[new_user.name] = new_user

                    #response = {"method": "accept_connection", "args": None};
                    response['players'][new_user.name] = {"status": "accept", "x": new_user.x, "y": new_user.y}
                    response["status"] = "accept"
                    # print(response);
                    self.buffer['players'][new_user.name] = {"x": new_user.x, "y": new_user.y, "O2": 100, "score": self.user_list[new_user.name].death_counter, "dead": self.user_list[new_user.name].dead}
                    
                else:
                    response = {"status": "reject", "args": {"reason": "duplicate name"}};

                self.sock.sendto(f"{len(json.dumps(response)):>16}{json.dumps(response)}".encode(), addr);

            elif(payload["method"] == "initialized"):
                pass;

            elif(payload["method"] == "disconnect"):
                pass;

            elif(payload["method"] == "send_player_update"):
                self.update_player_position(payload["args"], addr);
                
            elif(payload["method"] == "respawn"):
                self.update_player_position(payload["args"], addr, respawn=True)

                # response = {payload["args"]["username"]: {"x": self.user_list[payload["args"]["username"]].x, "y": self.user_list[payload["args"]["username"]].y}};

                # self.sock.sendto(json.dumps(response).encode(), addr);

            else:
                print("error", payload);
            




    def update_player_position(self, args, addr, respawn=False):
        username = args["username"];
        if not self.user_list[username]:
            self.user_list[username] = megalib.Player(name=username)
            self.user_list[username].ip_address = addr
        if respawn:
            self.user_list[username].x = 2255
            self.user_list[username].y = 365
            self.user_list[username].O2_level = 100
            self.user_list[username].death_counter += 1
            self.user_list[username].dead = False
        else:
            self.user_list[username].x = args["x"]
            self.user_list[username].y = args["y"]
        #print(args['x'], args['y']);
        #print(self.tank_list.O2_tanks[0].x*50+self.map_x_offset, self.tank_list.O2_tanks[0].y*48 +self.map_y_offset);
        # Check here for
        for tank in self.tank_list:
            if(args["x"] > (self.tank_list[tank]['x']*50+self.map_x_offset-50) and args["x"] < (self.tank_list[tank]['x']*50+self.map_x_offset + 100) and args["y"] > (self.tank_list[tank]['y']*48+self.map_y_offset-75) and args["y"] <(self.tank_list[tank]['y']*48+self.map_y_offset + 75)):
                self.buffer['tanks'][tank] = {"method": "delete"};
                # print('got me');
                self.tank_list.pop(tank);
                self.user_list[username].O2_level = self.user_list[username].O2_level + 20 if self.user_list[username].O2_level + 20 < 100 else 100
                #print("OP!!", tank, self.tank_list.pop(tank));
                break;
            #print(tank);
        self.buffer["players"][username] =  {"x": self.user_list[username].x, "y": self.user_list[username].y, "O2": self.user_list[username].O2_level, "dead": self.user_list[username].dead, "score": self.user_list[username].death_counter}










if __name__ == "__main__":
    server = GameServer(45000);
    server.start_server(); 