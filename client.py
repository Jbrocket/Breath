import pygame 
import sys 
import socket
import json

import megalib

global width
global height
global screen
  
class ClientSocket:
    
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port
        self.send_socket = None
        # self.recv_socket = None
        
    def connect(self, host=None, port=None, name="jbrock"):
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if host:
            self.host = host
        if port:
            self.port = port
            
        # self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_socket.bind(("", 0))
        
        return self.connect_ack(name)
        
    def connect_ack(self, name):
        msg = json.dumps({"method": "connect", "args": {"username": name, "recv_port": self.send_socket.getsockname()[1], "address": socket.gethostname()}})
        msg = f"{len(msg.encode()):>16}{msg}"
        self.send_socket.sendto(msg.encode(), (self.host, int(self.port)))
        
        data, addr = self.send_socket.recvfrom(65536)
        data = data[16:]
        data = json.loads(data.decode())
        return megalib.Player(name=name, x=data['x'], y=data['y'])
    
    def recv_mesg(self):
        data, addr = self.send_socket.recvfrom(65536)
        data = json.loads(data.decode())
        return data['x'], data['y']
        
    def send_data(self, move, name):
        msg = json.dumps({"method": "send_player_update", "args": {"username": name, "input": move}})
        msg = f"{len(msg.encode()):>16}{msg}"
        self.send_socket.sendto(msg.encode(), (self.host, int(self.port)))
        return self.recv_mesg()
        
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
                        me = client.connect(server, port, name=name)
                        connected = True
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_BACKSPACE:
                    if option == 1:
                        server = server[:-1]
                    elif option == 2:
                        port = port[:-1]
                    elif option == 3:
                        name = name[:-1]
                elif ev.unicode == "1":
                    option = 1
                elif ev.unicode == "2":
                    option = 2
                elif ev.unicode == "3":
                    option = 3
                else:
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
        
    in_game_loop(client, me)
    
def in_game_loop(client: ClientSocket, me: megalib.Player):
    clock = pygame.time.Clock()
    player_image = pygame.image.load("among_us.png").convert_alpha()
    player_image.set_colorkey((0, 0, 0))
    # player_image = player_image.get_rect()
    
    player_image = pygame.transform.rotozoom(player_image, 0, 1/5)
    
    while True:
        screen.fill((255,255,255))
        for ev in pygame.event.get(): 
            if ev.type == pygame.QUIT:
                pygame.quit()
            if ev.type == pygame.KEYDOWN:
                if ev.unicode == "w":
                    me.x, me.y = client.send_data("up", me.name)
                elif ev.unicode == "a":
                    me.x, me.y = client.send_data("left", me.name)
                elif ev.unicode == "s":
                    me.x, me.y = client.send_data("down", me.name)
                elif ev.unicode == "d":
                    me.x, me.y = client.send_data("right", me.name)
        screen.blit(player_image, (me.x, me.y))
        clock.tick(60)
        pygame.display.update()

def main():
    pygame.init()
    res = (600,500) 

    global width
    global height
    global screen
    
    screen = pygame.display.set_mode(res) 
    width = screen.get_width() 
    height = screen.get_height() 
    
    get_host_and_client()
    
if __name__ == "__main__":
    main()