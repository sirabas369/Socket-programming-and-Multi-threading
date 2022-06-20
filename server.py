import socket
import numpy as np
import threading
import copy
import time


map = np.array([['E','.','.','.','.','.','.','.','.','#'],
                ['.','#','.','#','.','.','.','.','.','#'],
                ['.','.','.','.','.','#','.','.','#','.'],
                ['.','.','.','.','.','.','.','.','.','.'],
                ['#','.','.','.','.','.','.','#','.','.'],
                ['.','.','.','.','#','.','.','.','.','.'],
                ['.','.','.','.','.','.','.','.','.','.'],
                ['#','.','.','.','.','.','.','#','.','.'],
                ['.','.','.','.','#','.','.','.','.','.'],
                ['S','.','#','.','.','.','.','#','.','.']] , dtype = object)
pos = [[0,0],[0,0],[0,0],[0,0]]

l = 1
h = 6

active_threads = []
alive_connections = {}
closed_connections = []
escaped = []

def communicate(conn):
    conn.sendall(str('\n').encode('utf-8'))
    vs = conn.recv(1024).decode()
    v = int(vs)
    return v


def check_explosion(x,y):
    global map
    if(map[9-y][x] == '#'):
        return True 
    else:
        return False

def move_back(x , y ,client_no):
    global pos
    new_pos = [x,y]

    if (y % 2 == 0):
        if ((x == 8) or (x == 9) ):
            new_pos[0] = x - 8
        else:
            diff = 8 - x
            new_pos[1] = y - 1
            new_pos[0] = diff - 1
    else:
        if ((x == 0) or (x == 1) ):
            new_pos[0] = x + 8
        else:
            diff = 8 - (9 - x)
            new_pos[1] = y - 1
            new_pos[0] = 10 - diff

    if ((y == 0) and (x < 8)):
        new_pos[0] = 0
        new_pos[1] = 0

    if check_explosion(new_pos[0],new_pos[1]):
        move_back(new_pos[0] , new_pos[1] , client_no)
    else:
        pos[client_no][0] = new_pos[0]
        pos[client_no][1] = new_pos[1]
    



def move(client_no, step, connection):
    global pos
    new_pos = copy.deepcopy(pos[client_no])
    if (pos[client_no][1] % 2 == 0):
        if ((pos[client_no][0] + step) <= 9):
            new_pos[0] = pos[client_no][0] + step
        else:
            diff = step - (9 - pos[client_no][0])
            new_pos[1] = pos[client_no][1] + 1
            new_pos[0] = 10 - diff
    else:
        if ((pos[client_no][0] - step) >= 0):
            new_pos[0] = pos[client_no][0] - step
        else:
            diff = step - pos[client_no][0]
            new_pos[1] = pos[client_no][1] + 1
            new_pos[0] = diff - 1
    
    if not check_explosion(new_pos[0],new_pos[1]):
        if (new_pos == [0,9]) or (new_pos[1]>9):
            new_pos = [0,9]
            pos[client_no] = new_pos
            closed_connections.append([client_no + 1])
            escaped.append([client_no , connection])
        else:
            pos[client_no] = new_pos
    else:
        move_back(new_pos[0] , new_pos[1] , client_no)


def execution(connection, idx):
    step = communicate(connection)
    move(idx,step,connection)


def startserver():
    server = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    server.bind((socket.gethostname() , 8080))
    server.listen(4)
    for i in range(0,4):
        clientsocket , address = server.accept()
        print(f"Connection Establised to address {address} with name {i+1}")
        alive_connections[i] = clientsocket
        clientsocket.sendall(str.encode("\n".join([str(l) , str(h) , str(i+1)])))

    

startserver()
while True:
    for idx,conn in alive_connections.items():
        new_thread = threading.Thread(target = execution,args = (conn,idx))
        active_threads.append(new_thread)
        new_thread.start()
    
    for th in active_threads:
        th.join()

    active_threads = []

    for idx,conn in escaped:
        conn.sendall(str("end").encode('utf-8'))
        del alive_connections[idx]

    esc = []
    for i,c in escaped:
        esc.append(str(i+1))

    if (len(esc) >= 1):
        for idx,conn in alive_connections.items():
            conn.sendall(str.encode(f"workers {esc} escaped"))

    temp = copy.deepcopy(map)
    for i in range(0,4):
        if not (pos[i] == [0,0] or pos[i] == [0,9]):
            if (temp[9-pos[i][1]][pos[i][0]] == '.'):
                temp[9-pos[i][1]][pos[i][0]] = str(i+1)
            else:
                temp[9-pos[i][1]][pos[i][0]] += str(i+1)
    print('--------------------------------------------------------------')
    print(temp)

    if (len(closed_connections) == 4):
        break

    escaped = []
    del temp

    time.sleep(1) # for feel good - to see procedural changes

print(f"Order of escape : {closed_connections} ")    


