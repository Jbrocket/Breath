import pygame 
import sys 
import socket
import json

global width
global height
global screen
  
class ClientSocket:
    
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port
        self.send_socket = None
        self.recv_socket = None
        
    def connect(self, host=None, port=None, name="jbrock"):
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if host:
            self.host = host
        if port:
            self.port = port
            
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket.bind(("127.0.0.1", 0))
        
        return self.connect_ack(name)
        
    def connect_ack(self, name):
        msg = json.dumps({"player": name, "recv_port": self.recv_socket.getsockname()[1], "address": socket.gethostname()})
        print(msg)
        self.send_socket.sendto(msg.encode(), (self.host, self.port))
        
        data, addr = self.recv_socket.recvfrom(65536)
        
        return data
    
    def recv_mesg(self):
        data, addr = self.recv_socket.recvfrom(65536)
        
        
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
    connected = False
    option = 1
    
    while True: 
        
        for ev in pygame.event.get(): 
            
            if ev.type == pygame.QUIT: 
                pygame.quit() 
                
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if not connected:
                    if width/2 <= mouse[0] <= width/2+140 and height/2 <= mouse[1] <= height/2+40: 
                        client.connect(server, port, "jbrock")
                        connected = True
                        # pygame.quit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_BACKSPACE:
                    if option == 1:
                        server = server[:-1]
                    else:
                        port = port[:-1]
                elif ev.unicode == "1":
                    option = 1
                elif ev.unicode == "2":
                    option = 2
                else:
                    if option == 1:
                        server += ev.unicode
                    else:
                        port += ev.unicode
                    
                    
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
        
        screen.blit(smallfont.render(server, True, color), (width/2-50, height/4))
        screen.blit(smallfont.render(port, True, color), (width/2-50, height/3))
        screen.blit(smallfont.render("1 server", True, color), (width/2-200, height/4))
        screen.blit(smallfont.render("2 port", True, color), (width/2-200, height/3))
        
        pygame.display.update()
    
def in_game_loop():
    pass

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