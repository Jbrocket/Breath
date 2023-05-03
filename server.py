import socket, json, time, threading, collections, os, copy;
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

    def check_point(self):
        while True:
            players = {}
            tanks = {}
            
            for player in self.user_list:
                players[player] = {'x': self.user_list[player].x, 'y': self.user_list[player].y, 'score': self.user_list[player].death_counter, 'dead': self.user_list[player].dead, 'O2': self.user_list[player].O2_level, 'ip_address': self.user_list[player].ip_address}
            for tank in self.tank_list:
                tanks[tank] = {'x': self.tank_list[tank]['x'], 'y': self.tank_list[tank]['y']}
            
            shadow = open('shadow.ckpt', 'w')
            shadow.write(json.dumps({'players': players, 'tanks': tanks}))
            shadow.flush()
            os.fsync(shadow)
            
            try:
                os.rename('json.ckpt', 'delete.me')
                os.remove('delete.me')
            except FileNotFoundError:
                pass
            
            shadow.close()
            os.rename('shadow.ckpt', 'json.ckpt')
            time.sleep(1)
        return

    def update_players(self):
        while True:
            user: megalib.Player
            for tank in self.buffer["tanks"]:
                self.buffer["tanks"][tank]['x'] = self.buffer["tanks"][tank]['x'] * 50 + self.map_x_offset
                self.buffer["tanks"][tank]['y'] = self.buffer["tanks"][tank]['y'] * 48 + self.map_y_offset
            if self.buffer["players"] or self.buffer["tanks"]:
                users = self.user_list.copy()
                for user in users:
                    if time.time() - self.user_list[user].last_heard_from > 20:
                        self.user_list[user].status = "offline"
                        self.buffer['players'][user] = {"status": "offline"}
                    else:
                        self.user_list[user].status = "online"
                for user in users:
                    self.sock.sendto(f"{json.dumps(self.buffer)}".encode(), self.user_list[user].ip_address)

                self.buffer = {"players": {}, "tanks": {}}
            time.sleep(0.00833)
        
        return
    
    def lower_oxygen(self):
        while True:
            
            for username in self.user_list:
                if self.user_list[username].status == "offline":
                    continue
                self.user_list[username].O2_level = self.user_list[username].O2_level - 5 if self.user_list[username].O2_level - 5 > 0 else 0
                if self.user_list[username].O2_level == 0:
                    self.user_list[username].dead = True
                    self.user_list[username].death_counter += 1
                self.buffer["players"][username] = {"x": self.user_list[username].x, "y": self.user_list[username].y, "O2": self.user_list[username].O2_level, "score": self.user_list[username].death_counter, "dead": self.user_list[username].dead}
            
            time.sleep(1)

    def get_prev_state(self):
        if os.path.isfile('json.ckpt') and os.path.isfile('shadow.ckpt'):
            os.remove('shadow.ckpt')
        elif os.path.isfile('shadow.ckpt') and not os.path.isfile('json.ckpt'):
            os.rename('shadow.ckpt', 'json.ckpt')
        elif os.path.isfile('json.ckpt'):
            pass
        else:
            return
        f = open('json.ckpt', 'r')
        data = json.load(f)
        
        self.user_list: dict[str, megalib.Player]
        for player in data['players']:
            self.user_list[player] = megalib.Player(player)
            self.user_list[player].x = data['players'][player]['x']
            self.user_list[player].y = data['players'][player]['y']
            self.user_list[player].death_counter = data['players'][player]['score']
            self.user_list[player].dead = data['players'][player]['dead']
            self.user_list[player].O2_level = data['players'][player]['O2']
            self.user_list[player].ip_address = tuple(data['players'][player]['ip_address'])
            self.user_list[player].status = "offline"
        self.tank_list = {}
        for tank in data['tanks']:
            self.tank_list[tank] = {'x': data['tanks'][tank]['x'], 'y': data['tanks'][tank]['y']}
        
        return
    
    def start_server(self):
        self.get_prev_state()


        host_name = socket.gethostname()
        ip_address = socket.gethostbyname(host_name)
        self.sock = socket.socket(type=socket.SOCK_DGRAM);
        self.sock.bind((ip_address, self.port_no));
        print(f"Listening on port {self.sock.getsockname()[1]}, on address {ip_address}")


        # Begin timer thread now
        t = threading.Thread(target=self.update_players, daemon=True)
        p = threading.Thread(target=self.lower_oxygen, daemon=True)
        c = threading.Thread(target=self.check_point, daemon=True)
        z = threading.Thread(target=self.new_tanks, daemon=True)
        z.start()
        c.start()
        p.start()
        t.start()
        
        while(True):
            msg, addr = self.sock.recvfrom(64000);
            size = int(msg.decode()[0:16]);
            payload = json.loads(msg.decode()[16:(16+size)]);


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
                    new_user.last_heard_from = time.time()
                    response = {"status": "accept", "players": {}, "tanks": {}}

                    user_list = self.user_list.copy()
                    tank_list = self.tank_list.copy()
                    for user in self.user_list:
                        if not self.user_list[user]:
                            continue
                        response['players'][user] = {"status": self.user_list[user].status, "x": self.user_list[user].x, "y": self.user_list[user].y, "dead": self.user_list[user].dead }
                    for tank in tank_list:
                        response['tanks'][tank] = {"x": self.tank_list[tank]['x']*50 + self.map_x_offset, "y":self.tank_list[tank]['y']*48 + self.map_y_offset};
                    self.user_list[new_user.name] = new_user

                    response['players'][new_user.name] = {"status": "accept", "x": new_user.x, "y": new_user.y}
                    response["status"] = "accept"
                    self.buffer['players'][new_user.name] = {"x": new_user.x, "y": new_user.y, "O2": 100, "score": self.user_list[new_user.name].death_counter, "dead": self.user_list[new_user.name].dead}
                
                elif self.user_list[payload["args"]["username"]].status == "offline":
                    self.user_list[payload["args"]["username"]].status = "online"
                    self.user_list[payload["args"]["username"]].ip_address = addr
                    self.user_list[payload["args"]["username"]].last_heard_from = time.time()
                    user_list = self.user_list.copy()
                    tank_list = self.tank_list.copy()
                    response = {"status": "accept", "players": {}, "tanks": {}}
                    
                    for user in user_list:
                        if not self.user_list[user]:
                            continue
                        response['players'][user] = {"status": self.user_list[user].status, "x": self.user_list[user].x, "y": self.user_list[user].y, "dead": self.user_list[user].dead, "O2": self.user_list[user].O2_level }
                    for tank in tank_list:
                        response['tanks'][tank] = {"x": self.tank_list[tank]['x']*50 + self.map_x_offset, "y":self.tank_list[tank]['y']*48 + self.map_y_offset};
                        
                else:
                    response = {"status": "reject", "args": {"reason": "duplicate name"}};

                self.sock.sendto(f"{len(json.dumps(response)):>16}{json.dumps(response)}".encode(), addr);

            elif(payload["method"] == "disconnect"):
                self.delete_player(payload["args"], addr)

            elif(payload["method"] == "send_player_update"):
                self.update_player_position(payload["args"], addr);
                
            elif(payload["method"] == "respawn"):
                self.update_player_position(payload["args"], addr, respawn=True)

            else:
                print("error", payload);
            


    def delete_player(self, args, addr):
        user = self.user_list[args["username"]]
        user.status = "offline"
        self.buffer['players'][user.name] = {'status': 'offline'}
        return

    def new_tanks(self):
        tankies = megalib.O2Tanks()
        while True:
            self.tank_list = {};
            tankies.create_tanks(10);
            for i in range(10):
                self.tank_list[i] = {"x": tankies.O2_tanks[i].x, "y": tankies.O2_tanks[i].y};
                
            for i in range(10):
                self.buffer["tanks"][i] = {"x": tankies.O2_tanks[i].x, "y": tankies.O2_tanks[i].y}
            time.sleep(15)
        return

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
            self.user_list[username].status = "online"
        else:
            self.user_list[username].x = args["x"]
            self.user_list[username].y = args["y"]

        self.user_list[username].last_heard_from = time.time()
        # Check here for
        for tank in self.tank_list:
            if(args["x"] > (self.tank_list[tank]['x']*50+self.map_x_offset-50) and args["x"] < (self.tank_list[tank]['x']*50+self.map_x_offset + 100) and args["y"] > (self.tank_list[tank]['y']*48+self.map_y_offset-75) and args["y"] <(self.tank_list[tank]['y']*48+self.map_y_offset + 75)):
                
                self.tank_list.pop(tank);
                self.buffer["tanks"] = copy.deepcopy(self.tank_list)
                self.user_list[username].O2_level = self.user_list[username].O2_level + 20 if self.user_list[username].O2_level + 20 < 100 else 100
                break;
        self.buffer["players"][username] =  {"x": self.user_list[username].x, "y": self.user_list[username].y, "O2": self.user_list[username].O2_level, "dead": self.user_list[username].dead, "score": self.user_list[username].death_counter}










if __name__ == "__main__":
    server = GameServer(45000);
    server.start_server(); 