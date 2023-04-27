import pygame 
import socket
import json
from threading import Thread
import collections
import time

from src import megalib

global width
global height
global screen
global player_image
global camera_x
global camera_y
global offset
  
class ClientSocket:
    
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port
        self.send_socket = None
        # self.recv_socket = None
        
    def connect(self, host=None, port=None, name="jbrock", game_state: dict = None):
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if host:
            self.host = host
        if port:
            self.port = port
            
        host_name = socket.gethostname()
        ip_address = socket.gethostbyname(host_name)
        self.send_socket.bind((ip_address, 0))
        return self.connect_ack(name, game_state=game_state)
        
    def connect_ack(self, name, game_state: dict):
        msg = json.dumps({"method": "connect", "args": {"username": name, "recv_port": self.send_socket.getsockname()[1], "address": socket.gethostname()}})
        msg = f"{len(msg.encode()):>16}{msg}"
        self.send_socket.sendto(msg.encode(), (self.host, int(self.port)))
        
        data, addr = self.send_socket.recvfrom(65536)
        data = data[16:]
        data = json.loads(data.decode())
        if data["status"] == "reject":
            return False
        
        game_state = {'me': "", 'tanks': collections.defaultdict(lambda: None), 'players': collections.defaultdict(lambda: None)}
        print(data['tanks']); 
        for user in data['players']:
            if user == name:
                game_state['me'] = megalib.Player(name=name, x=data['players'][user]['x'], y=data['players'][user]['y'])
            else:
                game_state['players'][user] = (megalib.Player(name=user, x = data['players'][user]['x'], y = data['players'][user]['y']))

        for tank in data['tanks']:
           game_state['tanks'][tank]= megalib.O2Tank(x=data['tanks'][tank]['x'], y=data['tanks'][tank]['y']);


        return game_state
    
    def recv_mesg(self, game_state: dict):
        
        while True:
            data, addr = self.send_socket.recvfrom(65536)
            data = json.loads(data.decode())
            if data['players']:
                for player, info in data['players'].items():
                    if player == game_state['me'].name:
                        game_state['me'].x, game_state['me'].y = info['x'], info['y']
                    else:
                        if not game_state['players'][player]:
                            game_state['players'][player] = megalib.Player(name=player, x=info['x'], y=info['x'])
                        else:
                            game_state['players'][player].x, game_state['players'][player].y = info['x'], info['y']
            if data['tanks']:
                print('hey');
                for tank, info in data['tanks'].items():
                    if info['method'] == "delete":
                        game_state['tanks'].pop(tank);
                        print(game_state['tanks']);
            time.sleep(0.0083)
        return
        
    def send_data(self, move, game_state):
        name = game_state['me'].name
        if(move == "up"):
            game_state['me'].move_up()
        elif(move == "down"):
            game_state['me'].move_down()
        elif(move == "left"):
            game_state['me'].move_left()
        elif(move == "right"):
            game_state['me'].move_right()
        msg = json.dumps({"method": "send_player_update", "args": {"username": name, "x": game_state['me'].x, "y": game_state['me'].y}})
        msg = f"{len(msg.encode()):>16}{msg}"
        self.send_socket.sendto(msg.encode(), (self.host, int(self.port)))
        
        return None
    
def render_map(game_state: dict):
    screen.blit(game_state['background'], (camera_x - width/2 - offset , camera_y - height/2 - offset))
    return

def display_characters(game_state: dict):
    smallfont = pygame.font.SysFont('Corbel',35)


    for tank in game_state['tanks']:
        screen.blit(tank_image, (game_state['tanks'][tank].x+ camera_x, game_state['tanks'][tank].y+camera_y))

    ### ME
    screen.blit(smallfont.render(game_state['me'].name, True, (100,100,100)), (game_state['me'].x + camera_x + 25, game_state['me'].y + camera_y - 10))
    screen.blit(player_image, (game_state['me'].x + camera_x, game_state['me'].y + camera_y))
    

    for player in game_state['players']:
        screen.blit(smallfont.render(game_state['players'][player].name, True, (100,100,100)), (game_state['players'][player].x + camera_x + 25, game_state['players'][player].y + camera_y - 10))
        screen.blit(player_image, (game_state['players'][player].x + camera_x, game_state['players'][player].y + camera_y))

    #for tank in game_state['tanks']:

    return
        
def get_host_and_client():
    color = (255,255,255) 
    color_light = (170,170,170) 
    color_dark = (100,100,100) 
    
    smallfont = pygame.font.SysFont('Corbel',35)
    text_connected = smallfont.render('connected' , True , color) 
    text_not_connected = smallfont.render('not connected' , True , color) 
    client = ClientSocket()
    server = ""
    port = ""
    name = ""
    connected = False
    option = 1
    
    while True: 
        
        for ev in pygame.event.get(): 
            
            if ev.type == pygame.QUIT: 
                pygame.quit() 
                
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if not connected:
                    if width/2 <= mouse[0] <= width/2+140 and height/2 <= mouse[1] <= height/2+40: 
                        game_state = client.connect(server, port, name=name, game_state={})
                        if not game_state:
                            continue
                        connected = True
                        me = game_state['me']
                        
            if ev.type == pygame.KEYDOWN:
                key_pressed = pygame.key.get_pressed()
                if ev.key == pygame.K_BACKSPACE:
                    if option == 1:
                        server = server[:-1]
                    elif option == 2:
                        port = port[:-1]
                    elif option == 3:
                        name = name[:-1]
                elif key_pressed[pygame.K_UP]:
                    option -= 1
                elif key_pressed[pygame.K_DOWN]:
                    option += 1
                else:
                    if option > 3:
                        option = 3
                    if option < 1:
                        option = 1
                        
                    if option == 1:
                        server += ev.unicode
                    elif option == 2:
                        port += ev.unicode
                    elif option == 3:
                        name += ev.unicode
                    
                    
        # fills the screen with a color 
        screen.fill((60,25,60)) 
        
        # stores the (x,y) coordinates into 
        # the variable as a tuple 
        mouse = pygame.mouse.get_pos() 
        
        # if mouse is hovered on a button it 
        # changes to lighter shade 
        if not connected:
            if width/2 <= mouse[0] <= width/2+140 and height/2 <= mouse[1] <= height/2+40: 
                pygame.draw.rect(screen,color_light,[width/2-50,height/2,140,40]) 
                
            else: 
                pygame.draw.rect(screen,color_dark,[width/2-50,height/2,140,40]) 
        
        # superimposing the text onto our button 
        if not connected:
            screen.blit(text_not_connected , (width/2-50,height/2)) 
        else:
            screen.blit(text_connected , (width/2-50,height/2)) 
        
        screen.blit(smallfont.render(server, True, color), (width/2-50, 1*height/10))
        screen.blit(smallfont.render(port, True, color), (width/2-50, 2*height/10))
        screen.blit(smallfont.render(name, True, color), (width/2-50, 3*height/10))
        screen.blit(smallfont.render("1 server", True, color), (width/2-200, height/10))
        screen.blit(smallfont.render("2 port", True, color), (width/2-200, 2*height/10))
        screen.blit(smallfont.render("3 name", True, color), (width/2-200, 3*height/10))
        
        
        pygame.display.update()
        if connected:
            break
        
    in_game_loop(client, me, game_state=game_state)
    
    
def in_game_loop(client: ClientSocket, me: megalib.Player, game_state: dict):
    global player_image
    global tank_image
    global camera_x
    global camera_y
    global offset
        
    game_state['background'] = pygame.image.load("./src/among-us-map.jpg").convert_alpha()
    game_state['background'] = pygame.transform.rotozoom(game_state['background'], 0, 3.5)
    clock = pygame.time.Clock()
    player_image = pygame.image.load("./src/among_us.png").convert_alpha()
    player_image.set_colorkey((0, 0, 0))
    # player_image = player_image.get_rect()
    
    player_image = pygame.transform.rotozoom(player_image, 0, 1/5)

    tank_image = pygame.image.load("./src/oxygen.webp");
    tank_image = pygame.transform.rotozoom(tank_image, 0, 1/5);

    mov_types = {"up": False, "down": False, "left": False, "right": False}
    
    t = Thread(target=client.recv_mesg, daemon=True, args=[game_state])
    t.start()
    
    offset = - 50
    camera_x = width / 2  + offset
    camera_y = height / 2 + offset
    
    while True:
        screen.fill((255,255,255))
        render_map(game_state)
        
        for ev in pygame.event.get(): 
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.KEYDOWN:
                if ev.unicode == "w":
                    mov_types['down'] = True
                elif ev.unicode == "a":
                    mov_types['left'] = True
                elif ev.unicode == "s":
                    mov_types['up'] = True
                elif ev.unicode == "d":
                    mov_types['right'] = True
            if ev.type == pygame.KEYUP:
                if ev.unicode == "w":
                    mov_types['down'] = False
                elif ev.unicode == "a":
                    mov_types['left'] = False
                elif ev.unicode == "s":
                    mov_types['up'] = False
                elif ev.unicode == "d":
                    mov_types['right'] = False
                    
        for mov in mov_types:
            if mov_types[mov]: 
                client.send_data(mov, game_state)
                
                # client.recv_mesg(game_state=game_state)
        
        if (game_state['me'].x + camera_x) >  width/2 + 30:
            camera_x -= (game_state['me'].x + camera_x) - (width/2 + 30)
        if (game_state['me'].x + camera_x) < width/2 - 100:
            camera_x += -(game_state['me'].x + camera_x) + (width/2 - 100)
        if (game_state['me'].y + camera_y) > height/2 + 30:
            camera_y -= (game_state['me'].y + camera_y) - (height/2 + 30)
        if (game_state['me'].y + camera_y) < height/2 - 100:
            camera_y += -(game_state['me'].y + camera_y) + (height/2 - 100)
        
        display_characters(game_state=game_state)
        clock.tick(60)
        pygame.display.update()

def main():
    pygame.init()
    res = (1000, 720) 

    global width
    global height
    global screen
    
    screen = pygame.display.set_mode(res) 
    width = screen.get_width() 
    height = screen.get_height() 
    get_host_and_client()
    
if __name__ == "__main__":
    main()