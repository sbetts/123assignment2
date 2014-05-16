## Whale Bot Client Edition
## Scott Betts; 76651961

## Original code by Thomas Debeauvais


from random import choice
from time import sleep


from network import Handler, poll
from pygame import Rect



borders = []
pellets = []
players = {}
myname = None
cmd = 'up'
game_status = True

def make_rect(quad): # make a pygame.Rect from a list of 4 integers
    x, y, w, h = quad
    return Rect(x, y, w, h)



class Client(Handler):
            
    def on_msg(self, data):
        global borders, pellets, players, myname
        borders = [make_rect(b) for b in data['borders']]
        if pellets != [make_rect(p) for p in data['pellets']] and pellets != []:
            print('Ate a pellet.')
        pellets = [make_rect(p) for p in data['pellets']]
        players = {name: make_rect(p) for name, p in data['players'].items()}
        myname = data['myname']

    def on_close(self):
        global game_status
        print('Server closed connection.')
        game_status = False
        
client = Client('localhost', 8888)
print('Connected to server.')
sleep(0.1)


        
################### CONTROLLER #############################

class SmartBotController():
        
    def poll(self):
        global cmd
        p = pellets[0] # always target the first pellet
        b = players[myname]
        if p[0] > b[0]:
            cmd = 'right'
        elif p[0] + p[2] <= b[0]: # p[2] to avoid stuttering left-right movement
            cmd = 'left'
        elif p[1] > b[1] and p[1] > b[1] - b[3]:
            cmd = 'down'
        else:
            cmd = 'up'
        client.do_send({'input': cmd})

################### CONSOLE VIEW #############################

class ConsoleView():
    def __init__(self):
        self.frame_freq = 20
        self.frame_count = 0
        
    def display(self):
        self.frame_count += 1
        if self.frame_count == self.frame_freq:
            self.frame_count = 0
            b = players[myname]
            


################### PYGAME VIEW #############################
# this view is only here in case you want to see how the bot behaves

import pygame

class PygameView():
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        
    def display(self):
        pygame.event.pump()
        screen = self.screen
        b = players[myname]
        myrect = pygame.Rect(b[0], b[1], b[2], b[3])
        screen.fill((0, 0, 64)) # dark blue
        pygame.draw.rect(screen, (0, 191, 255), myrect) # Deep Sky Blue
        [pygame.draw.rect(screen, (255, 192, 203), p) for p in pellets] # pink
        [pygame.draw.rect(screen, (0, 191, 255), b) for b in borders] # red
        pygame.display.update()
        
################### LOOP #############################

c = SmartBotController()
v = ConsoleView()
#v2 = PygameView()

while 1:
    if game_status == False:
        exit()
    sleep(0.02)
    poll()
    c.poll()
    v.display()
    #v2.display()
