#import modules needed
import random
import time
import math
import os
import pygame
import sys
from copy import deepcopy
import functools

#settings
WIDTH = 800
HEIGHT = 600
FPS = 30

BLACK = (0, 0, 0)
YELLOW = (255, 250, 2)
GREEN = (132, 244, 82)
BLUE = (0, 0, 255)
RED = (254,10,13)

def base_path(path):
  if getattr(sys, 'frozen', None):
    basedir = sys._MEIPASS
  else:
    basedir = os.path.dirname(__file__)
  return os.path.join(basedir, path)

cover = pygame.image.load(base_path('cover.jpg'))
bg = pygame.image.load(base_path('bg.jpg'))
bg_s = pygame.image.load(base_path('bg_settings.jpg'))
src_list = {1:'noodle_y.jpg',2:'laptop_y.jpg',3:'jacket_y.jpg',4:'gun_y.jpg',5:'glass_y.jpg',6:'motor_y.jpg',7:'police_y.jpg',8:'scary_y.jpg',9:'mask_y.jpg','x':'block.png'}
src_r_list = {1:'noodle_r.jpg',2:'laptop_r.jpg',3:'jacket_r.jpg',4:'gun_r.jpg',5:'glass_r.jpg',6:'motor_r.jpg',7:'police_r.jpg',8:'scary_r.jpg',9:'mask_r.jpg','x':'block.png'}

#init
pygame.font.init()
font = pygame.font.Font(base_path('consola.ttf'), 36)
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CYBERPUNK LINK GAME")
clock = pygame.time.Clock()
gameMode = 'start'
lastMode = None
flush = True
global inputMode
global c_string
global r_string
global t_string
global m_string
global data
data = {'pause':False, 'map':None, 'solution':None, 'size':None, 'type_n':None, 'timer':0.0, 'time':0.0, \
    'block_size':40, 'click_whom':None, 'search':True, 'score':0, 'solution':None, 'finish':False, 'click_solution':None}
c_string = None
r_string = None
t_string = None
m_string = None
inputMode = None
valid_inputs = [pygame.K_0,pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9,pygame.K_BACKSPACE,pygame.K_x]
input_map = {pygame.K_0:'0',pygame.K_1:'1',pygame.K_2:'2',pygame.K_3:'3',pygame.K_4:'4',pygame.K_5:'5',pygame.K_6:'6',pygame.K_7:'7',pygame.K_8:'8',pygame.K_9:'9',pygame.K_x:'x'}
img_list = {}
img_r_list = {}
for key,value in src_list.items():
    temp = pygame.image.load(base_path(src_list[key]))
    temp = pygame.transform.scale(temp, (data['block_size'],data['block_size']))
    img_list[key] = (temp)
for key,value in src_r_list.items():
    temp = pygame.image.load(base_path(src_r_list[key]))
    temp = pygame.transform.scale(temp, (data['block_size'],data['block_size']))
    img_r_list[key] = (temp)


#class
class Button():
    def __init__(self, size, loc, img=None, text=None, color=None):
        self.size = size
        self.loc = loc
        if img is not None:
            self.img = img
        if text is not None:
            self.img = pygame.font.Font.render(font,text, True, color)
            self.img = pygame.transform.scale(self.img, size)
        self.region = [self.loc[1], self.loc[1]+self.size[1],\
            self.loc[0], self.loc[0]+self.size[0]]

    def render(self):
        screen.blit(self.img, self.loc)
    
    def check_click(self, click_pos):
        check_x = (click_pos[0]>self.region[2]) & (click_pos[0]<self.region[3])
        check_y = (click_pos[1]>self.region[0]) & (click_pos[1]<self.region[1])
        if check_x and check_y:
            return True
        else:
            return False
        
@functools.total_ordering
class Node():
    def __init__(self, loc, dir, depth, turns, cost):
        self.loc = loc
        self.dir = dir
        self.depth = depth
        self.turns = turns
        self.cost = cost

    def __eq__(self, o: object) -> bool:
        return o.loc == self.loc

    def __gt__(self, other):
        return self.cost < other.cost

class TreeNode():
    def __init__(self,map_in, cost, parent, action):
        self.map =map_in
        self.cost = cost
        self.parent = parent
        self.action = action
    
    def __eq__(self, o: object) -> bool:
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if o.map[i][j] != self.map[i][j]:
                    return False
        return True
    

class SolutionPair():
    def __init__(self, x1, y1, x2, y2, cost):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.cost = cost

    def __eq__(self, o: object) -> bool:
        if self.x1 == o.x1 and self.x2 == o.x2 and self.y1 == o.y1 and self.y2 == o.y2:
            return True
        if self.x1 == o.x2 and self.x2 == o.x1 and self.y1 == o.y2 and self.y2 == o.y1:
            return True
        return False

class PQ():
    def __init__(self):
        self.data = []

    def get(self):
        cost = 1000000
        idx = 0
        for i in range(len(self.data)):
            if (self.data[i].cost < cost):
                cost = self.data[i].cost
                idx = i
        temp = self.data[idx]
        self.data.pop(idx)
        return temp
    
    def put(self, inp):
        self.data.append(inp)
    
    def check(self, inp):
        for i in range(len(self.data)):
            if self.data[i] == inp:
                if inp.cost < self.data[i].cost:
                    self.data[i] = inp
                return True
        return False

    def empty(self):
        return len(self.data) == 0


def get_map():
    global data
    m = []
    for i in range(data['size'][1]+2):
        m.append(0)
    map_in = [m]
    for i in range(data['size'][0]):
        temp_map = [0]
        for j in range(data['size'][1]):
            temp_map.append(data['map'][i*data['size'][1]+j])
        temp_map.append(0)
        map_in.append(temp_map)
    map_in.append(m)
    return map_in


def search(map_in, ans, closed, mode):
    if mode == '1':
        init_node = TreeNode(map_in, 10000, None, None)
    else:
        init_node = TreeNode(map_in, 0, None, None)

    def checkAndReplace(childNode, open, closed):
        res = False
        if open.check(childNode):
            res = True
        try:
            if closed[str(childNode.map)] == True:
                res = True
        except:
            pass
        return res

    def check(in_map):
        for i in range(len(in_map)):
            for j in range(len(in_map[i])):
                if in_map[i][j] != 'x' and in_map[i][j] != 0:
                    return False
        return True

    open = PQ()
    closed = {}
    open.put(init_node)
    while not open.empty():
        temp_node = open.get()
        if check(temp_node.map):
            cursor = temp_node
            while cursor.action is not None:
                ans.append(cursor.action)
                cursor = cursor.parent
            return True
        closed[str(temp_node.map)] = True
        child = []
        childList = []
        for i in range(data['size'][0]):
            for j in range(data['size'][1]):
                target = temp_node.map[i+1][j+1]
                if  target == 'x' or target == 0:
                    continue 
                init_node = Node([i+1,j+1],0,0,0,0)
                ans_list = ufc(temp_node.map, target, init_node, 3 if mode == '1' else None)

                for item in ans_list:
                    if not(item in child):
                        child.append(item)
                        temp_map = deepcopy(temp_node.map)
                        temp_map[item.x1][item.y1] = 0
                        temp_map[item.x2][item.y2] = 0
                        if mode == '1':
                            temp_treenode = TreeNode(temp_map, temp_node.cost - 1, temp_node, item)
                        else:
                            temp_treenode = TreeNode(temp_map, item.cost+temp_node.cost, temp_node, item)
                        childList.append(temp_treenode)

        for childNode in childList:
            if not(checkAndReplace(childNode, open, closed)):
                open.put(childNode)

    return False



def init_map(mode):
    global data
    condition1 = data['type_n'] is not None
    condition2 = data['size'] is not None
    if not(condition2 and condition1):
        return False
    condition3 = ((data['size'][0]) * (int(data['size'][1]))) % 2 == 0
    if not condition3:
        return False
    tempmap = []
    if data['map'] is not None:
        for i in range(len(data['map'])):
            if not data['map'][i] == 'x' and (int(data['map'][i]) >= int(data['type_n'])):
                return False
            if data['map'][i] == 'x':
                tempmap.append('x')
            else:
                tempmap.append(int(data['map'][i]))
        data['map'] = tempmap
        return True
    temp_counter = 0
    for i in range(int((int(data['size'][0])) * (int(data['size'][1])) / 2)):
        tempmap.append(temp_counter)
        tempmap.append(temp_counter)
        temp_counter += 1
        temp_counter = temp_counter % int(data['type_n'])
    random.shuffle(tempmap)
    if mode == 'gaming3':
        for i in range(len(tempmap)):
            if tempmap[i] == 0:
                tempmap[i] = 'x'
    data['map'] = tempmap

    return True


def ufc(in_map, target, init_node, limit):
    ans = []
    def check(childNode, open, close):
        ans = False
        if open.check(childNode):
            ans = True
        loc = str(childNode.loc[0])+str(childNode.loc[1])
        try:
            if close[loc] == True:
                ans = True
        except:
            pass
        return ans

    global data
    open = PQ()
    closed = {}
    open.put(init_node)
    while not open.empty():
        temp_node = open.get()
        if target == in_map[temp_node.loc[0]][temp_node.loc[1]] and (temp_node.dir != 0):
            temp_pair = SolutionPair(init_node.loc[0],init_node.loc[1],temp_node.loc[0],temp_node.loc[1],temp_node.turns)
            if not (temp_pair in ans):
                ans.append(temp_pair)
                continue
        closed[str(temp_node.loc[0])+str(temp_node.loc[1])] = True
        for i in range(1,5):
            temp_loc = deepcopy(temp_node.loc)
            if i == 1:
                temp_loc[0] += 1
            elif i == 2:
                temp_loc[1] += 1
            elif i == 3:
                temp_loc[0] -= 1
            elif i == 4:
                temp_loc[1] -= 1
            if temp_node.dir != 0 and temp_node.dir != i:
                temp_turn = temp_node.turns + 1
            elif temp_node.dir == 0:
                temp_turn = 0
            else:
                temp_turn = temp_node.turns
            if temp_node.dir != 0 and abs(temp_node.dir - i) == 2:
                continue
            childNode = Node(temp_loc, i, temp_node.depth+1, temp_turn, temp_turn)
            condition1 = childNode.loc[0] >= 0 and childNode.loc[0] <= data['size'][0] + 1
            condition2 = childNode.loc[1] >= 0 and childNode.loc[1] <= data['size'][1] + 1
            if not(condition1 and condition2):
                continue
            if limit is None:
                condition3 = True
            else:
                condition3 = childNode.turns < limit
            condition4 = in_map[childNode.loc[0]][childNode.loc[1]] != 'x'
            condition5 = childNode.depth == 1 or in_map[temp_node.loc[0]][temp_node.loc[1]] == 0
            if not(condition3 and condition4 and condition5):
                continue
            if not check(childNode, open, closed):
                open.put(childNode)
    return ans

def start_screen():
    screen.blit(cover, (0, 0))
    tempMode = 'start'
    play_button = Button((200,80), (100,400),text='play',color=GREEN)
    exit_button = Button((200,80),(500,400),text='exit',color=GREEN)

    if play_button.check_click(pygame.mouse.get_pos()):
        play_button = Button((180,80), (100,400),text='play',color=YELLOW)

    if exit_button.check_click(pygame.mouse.get_pos()):
        exit_button = Button((180,80),(500,400),text='exit',color=YELLOW)    

    play_button.render()
    exit_button.render()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if pygame.mouse.get_pressed()[0]:
            if play_button.check_click(pygame.mouse.get_pos()):
                tempMode = 'settings'
            if exit_button.check_click(pygame.mouse.get_pos()):
                pygame.quit()
                raise SystemExit
    return tempMode

def settings():
    screen.blit(bg_s, (0, 0))
    global c_string
    global r_string
    global m_string
    global t_string
    global inputMode
    global data

    tempMode = 'settings'
    back_button = Button((110,50),(100,500),text='back',color=GREEN)
    col_button = Button((180,50),(100,150),text='set cols',color=GREEN)
    row_button = Button((180,50), (100,75),text='set rows',color=GREEN)
    type_button = Button((110,50),(100,225),text='type',color=GREEN)
    map_button = Button((100,50),(100,300),text='map',color=GREEN)
    start1_button = Button((70,50),(100,400),text='Q1',color=GREEN)
    start2_button = Button((70,50),(350,400),text='Q2',color=GREEN)
    start3_button = Button((70,50),(600,400),text='Q3',color=GREEN)

    if start1_button.check_click(pygame.mouse.get_pos()):
        start1_button = Button((60,50),(100,400),text='Q1',color=YELLOW)
    if start2_button.check_click(pygame.mouse.get_pos()):
        start2_button = Button((60,50),(350,400),text='Q2',color=YELLOW)
    if start3_button.check_click(pygame.mouse.get_pos()):
        start3_button = Button((60,50),(600,400),text='Q3',color=YELLOW)
    if back_button.check_click(pygame.mouse.get_pos()):
        back_button = Button((90,50),(100,500),text='back',color=YELLOW)

    if r_string is not None:
        length = len(r_string)
        r_text = Button((20*length,50), (300,75),text=r_string,color=GREEN)
        r_text.render()

    if c_string is not None:
        length = len(c_string)
        c_text = Button((20*length,50),(300,150),text=c_string,color=GREEN)
        c_text.render()
    
    if t_string is not None:
        length = len(t_string)
        t_text = Button((20*length,50),(230,225),text=t_string,color=GREEN)
        t_text.render()

    if m_string is not None:
        length = len(m_string)
        m_text = Button((10*length,25),(230,320),text=m_string,color=GREEN)
        m_text.render()

    if inputMode == 'row':
        row_button = Button((150,50), (100,75),text='set rows',color=YELLOW)
    elif inputMode == 'col':
        col_button = Button((150,50),(100,150),text='set cols',color=YELLOW)
    elif inputMode == 'type':
        type_button = Button((90,50),(100,225),text='type',color=YELLOW)
    elif inputMode == 'map':
        map_button = Button((80,50),(100,300),text='map',color=YELLOW)


        
    row_button.render()
    col_button.render()
    back_button.render()
    start1_button.render()
    start2_button.render()
    start3_button.render()
    type_button.render()
    map_button.render()

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if pygame.mouse.get_pressed()[0]:
            if back_button.check_click(pygame.mouse.get_pos()):
                tempMode = 'start'
            if col_button.check_click(pygame.mouse.get_pos()):
                inputMode = 'col'
            if row_button.check_click(pygame.mouse.get_pos()):
                inputMode = 'row'
            if type_button.check_click(pygame.mouse.get_pos()):
                inputMode = 'type'
            if map_button.check_click(pygame.mouse.get_pos()):
                inputMode = 'map'
            if start1_button.check_click(pygame.mouse.get_pos()):
                tempMode = 'gaming1'
            if start2_button.check_click(pygame.mouse.get_pos()):
                tempMode = 'gaming2'
            if start3_button.check_click(pygame.mouse.get_pos()):
                tempMode = 'gaming3'
            if not(col_button.check_click(pygame.mouse.get_pos()) or row_button.check_click(pygame.mouse.get_pos())\
                or type_button.check_click(pygame.mouse.get_pos()) or map_button.check_click(pygame.mouse.get_pos())):
                inputMode = None
        if event.type == pygame.KEYDOWN:
            if event.key in valid_inputs and inputMode is not None:
                if inputMode == 'row':
                    temp_string = r_string
                elif inputMode == 'type':
                    temp_string = t_string
                elif inputMode == 'map':
                    temp_string = m_string
                elif inputMode == 'col':
                    temp_string = c_string 
                if temp_string is None:
                    if event.key is not pygame.K_BACKSPACE:
                        temp_string = input_map[event.key]
                elif len(temp_string) == 1:
                    if event.key is pygame.K_BACKSPACE:
                        temp_string = None
                    else:
                        temp_string += input_map[event.key]
                else:
                    if event.key is pygame.K_BACKSPACE:
                        temp_string = temp_string[:-1]
                    else:
                        temp_string += input_map[event.key]
                if inputMode == 'row':
                    r_string = temp_string
                elif inputMode == 'col':
                    c_string = temp_string
                elif inputMode == 'type':
                    t_string = temp_string
                elif inputMode == 'map':
                    m_string = temp_string
    if m_string is not None:
        data['map'] = m_string
    if c_string is not None and r_string is not None:
        data['size'] = (int(r_string), int(c_string))
    if t_string is not None:
        data['type_n'] = int(t_string)
    return tempMode

def warning(game):
    screen.blit(bg, (0, 0))
    global data
    back_button = Button((150,80),(500,500),text='back',color=GREEN)
    confirm_buttion = Button((280,80),(100,500),text='continue',color=GREEN)
    warning_text1 = Button((320,80),(250,100),text='Warning!',color=RED)
    warning_text2 = Button((700,60),(50,250),text='illegal input detected',color=RED)
    warning_text3 = Button((600,60),(100,400),text='use default settings?',color=RED)
    if back_button.check_click(pygame.mouse.get_pos()):
        back_button = Button((130,80),(500,500),text='back',color=YELLOW)
    if confirm_buttion.check_click(pygame.mouse.get_pos()):
        confirm_buttion = Button((260,80),(100,500),text='continue',color=YELLOW)

    warning_text1.render()
    warning_text2.render()
    warning_text3.render()
    back_button.render()
    confirm_buttion.render()
    
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if pygame.mouse.get_pressed()[0]:
            if back_button.check_click(pygame.mouse.get_pos()):
                game = 'settings'
            if confirm_buttion.check_click(pygame.mouse.get_pos()):
                if data['type_n'] is None and data['size'] is None:
                    data['type_n'] = 4
                    data['size'] = (4,4)
                if data['size'] is None:
                    data['size'] = (data['type_n'], 4)
                if (data['size'][0] * data['size'][1]) % 2 != 0:
                        data['size'] = (4,4)
                if data['type_n'] is None:
                    data['type_n'] = 4
                data['map'] = None

                game = 'gaming'+ game[-1]
    
    return game

def gaming(game):
    global data
    screen.blit(bg, (0, 0))
    mode = game[-1]

    if data['pause']:
        pause_text = Button((350,100),(250,250),text='pause!',color=GREEN)
        resume_button = Button((350,100),(250,450),text='resume',color=GREEN)
        if resume_button.check_click(pygame.mouse.get_pos()):
            resume_button = Button((300,100),(250,450),text='resume',color=YELLOW)

        pause_text.render()
        resume_button.render()
        data['timer'] = time.time()
    elif data['finish']:
        back_button = Button((200,100),(300,450),text='back',color=GREEN)
        score_text = Button((300,100),(250,250),text='score:'+str(data['score']),color=GREEN)

        if back_button.check_click(pygame.mouse.get_pos()):
            back_button = Button((200,100),(300,450),text='back',color=YELLOW)
        back_button.render()
        score_text.render()
    else:
        pause_button = Button((110,40),(50,500),text='pause',color=GREEN)
        back_button = Button((100,40),(650,500),text='back',color=GREEN)
        hint_button = Button((90,40),(350,500),text='hint',color=GREEN)
        if back_button.check_click(pygame.mouse.get_pos()):
            back_button = Button((90,40),(650,500),text='back',color=YELLOW)
        if pause_button.check_click(pygame.mouse.get_pos()):
            pause_button = Button((100,40),(50,500),text='pause',color=YELLOW)
        if hint_button.check_click(pygame.mouse.get_pos()):
            hint_button = Button((80,40),(350,500),text='hint',color=YELLOW)
        data['time'] += time.time() - data['timer']
        data['timer'] = time.time()
        time_text = Button((140,35),(600,30),text='time:'+str(math.floor(data['time'])),color=GREEN)
        score_text = Button((150,35),(30,30),text='score:'+str(data['score']),color=GREEN)
        item_list = []
        start_point = [400-data['size'][1]/2*data['block_size'],300-data['size'][1]/2*data['block_size']]
        pygame.draw.rect(screen, GREEN,[start_point[0]-20, start_point[1]-20, data['size'][1]*data['block_size']+40, data['size'][0]*data['block_size']+40])
        pygame.draw.rect(screen, BLACK,[start_point[0]-15, start_point[1]-15, data['size'][1]*data['block_size']+30, data['size'][0]*data['block_size']+30])
        for i in range(len(data['map'])):
            row = math.floor(i/data['size'][1])
            col = i % data['size'][1]
            if data['map'][i] != 0:
                item_list.append(Button((data['block_size'],data['block_size']),(start_point[0]+col*data['block_size'],start_point[1]+row*data['block_size']),img=img_list[data['map'][i]]))
            else:
                item_list.append(Button((data['block_size'],data['block_size']),(start_point[0]+col*data['block_size'],start_point[1]+row*data['block_size']),text=str(data['map'][i]),color=GREEN))
            if i == data['click_whom'] and data['map'][data['click_whom']] != 0:
                item_list[i] = Button((data['block_size'],data['block_size']),(start_point[0]+col*data['block_size'],start_point[1]+row*data['block_size']),img=img_r_list[data['map'][i]])
            if data['map'][i] != 0:
                item_list[-1].render()

        hint_button.render()
        time_text.render()
        score_text.render()
        pause_button.render()
        back_button.render()
    
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if pygame.mouse.get_pressed()[0]:
            pressItem = False
            if data['pause']:
                if resume_button.check_click(pygame.mouse.get_pos()):
                    data['pause'] = False
            elif data['finish']:
                if back_button.check_click(pygame.mouse.get_pos()):
                    game = 'start'
            else:
                if hint_button.check_click(pygame.mouse.get_pos()):
                    temp_solution = data['solution'][-1]
                    pos1 = (temp_solution.x1-1)*data['size'][1] + temp_solution.y1 - 1
                    pos2 = (temp_solution.x2-1)*data['size'][1] + temp_solution.y2 - 1
                    data['solution'] = data['solution'][:-1]
                    data['map'][pos1] = 0
                    data['map'][pos2] = 0
                if back_button.check_click(pygame.mouse.get_pos()):
                    game = 'start'
                if pause_button.check_click(pygame.mouse.get_pos()):
                    data['pause'] = True
                for i in range(len(item_list)):
                    if item_list[i].check_click(pygame.mouse.get_pos()):
                        if data['click_whom'] is not None:
                            row = math.floor(i/data['size'][1]) + 1
                            col = i % data['size'][1] + 1
                            if [row, col] in data['click_solution']:
                                data['map'][data['click_whom']] = 0
                                data['map'][i] = 0
                                data['score'] += 10
                                data['search'] = True
                        else:
                            if not(data['map'][i] in ['x',0]):
                                data['click_whom'] = i
                                row = math.floor(data['click_whom']/data['size'][1])
                                col = data['click_whom'] % data['size'][1]
                                init_node = Node([row+1,col+1],0,0,0,0)
                                temp_ans = ufc(get_map(),data['map'][data['click_whom']],init_node, 3 if mode == '1' else None)
                                data['click_solution'] = []
                                for item in temp_ans:
                                    data['click_solution'].append([item.x2,item.y2])
                                pressItem = True
            if pressItem == False:
                data['click_whom'] = None
                data['click_solution'] = None
    
    sum_n = 0
    for i in range(len(data['map'])):
        if data['map'][i] != 'x':
            sum_n += data['map'][i]
    if sum_n == 0:
        data['finish'] = True
        return game

    if data['search']:
        solution = []
        closed = {}
        while True:
            map_in = get_map()

            if search(map_in, solution, closed, mode):
                break
            random.shuffle(data['map'])

        data['solution'] = solution
        data['search'] = False
        
    return game

while True:
    if gameMode == 'start':
        if flush:
            data['type_n'] = None
            data['size'] = None
            data['map'] = None
        gameMode = start_screen()
    elif gameMode == 'settings':
        if flush:
            c_string = None
            r_string = None
            m_string = None
            t_string = None
        gameMode = settings()
    elif 'gaming' in gameMode:
        success = True
        if flush:
            data['timer'] = time.time()
            data['time'] = 0.0
            data['finish'] = False
            data['click_whom'] = None
            data['score'] = 0
            data['solution'] = None
            data['search'] = True
            success = init_map(gameMode)
            if not success:
                gameMode = 'warning' + gameMode[-1]
        if success:
            gameMode = gaming(gameMode)
    elif 'warning' in gameMode:
        if flush:
            screen.fill(BLACK)
        gameMode = warning(gameMode)

    flush = lastMode!=gameMode
    clock.tick(FPS)
    pygame.display.flip()
    lastMode = gameMode

