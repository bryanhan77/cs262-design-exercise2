from multiprocessing import Process
import os
import socket
from _thread import *
import threading
import time
from threading import Thread
import random
 

# each consumer is a server
def consumer(conn):
    print("[CONSUMER] new thread for client " + str(conn) + "\n")
    msg_queue=[]
    # should be different for every machine
    sleepVal = 5
    while True:
        time.sleep(sleepVal)
        data = conn.recv(1024)
        print("msg received\n")
        dataVal = data.decode('ascii')
        print("msg received:", dataVal)
        msg_queue.append(dataVal)
 

# each producer is a client
def producer(portVal):
    ADDR = "127.0.0.1"
    PORT = int(portVal)
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sleepVal = 5
    #sema acquire
    try:
        s.connect((ADDR, PORT))
        print("[PRODUCER] Connected to port: " + str(PORT) + "\n")
        
        while True:
            codeVal = str(code)
            time.sleep(sleepVal)
            s.send(codeVal.encode('ascii'))
            print("msg sent", codeVal)

    except socket.error as e:
        print("Error connecting producer: %s" % e)
 

# initialize listening server for each machine
def init_machine(config):
    # config: [address, listening port, connected port, process id]
    ADDR, PORT = str(config[0]), int(config[1])
    PID = str(config[3])
    
    print("[INIT MACHINE] Listening on port: " + str(PORT) + " for process: " + PID + "\n")
    print("clockrate: " + str(clockrate) + "\n")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ADDR, PORT))
    server.listen()

    while True:
        conn, addr = server.accept()
        # start consumer thread for every consumer
        start_new_thread(consumer, (conn,))
 

# individual machine process
def machine(config):
    # config: [address, server port, client port, process id]
    config.append(os.getpid())

    # randomized message
    global code

    # declare clockrate between 1 and 6 (actions per second)
    global clockrate 
    clockrate = random.randint(1,6)

    # need a clockrate between 1-6 (# of instructions per second)
    

    print("[MACHINE] config: " + str(config) + "\n")
    
    # thread for listening
    init_thread = Thread(target=init_machine, args=(config,))
    init_thread.start()
    #add delay to initialize the server-side logic on all processes
    time.sleep(5)

    # extensible to multiple producers
    prod_thread = Thread(target=producer, args=(config[2],))
    prod_thread.start()
    
    while True:
        code = random.randint(1,3)



localHost= "127.0.0.1"
    
if __name__ == '__main__':
    port1 = 18001
    port2 = 28001
    port3 = 38001
    
    config1=[localHost, port1, port2]
    p1 = Process(target=machine, args=(config1,))

    config2=[localHost, port2, port3]
    p2 = Process(target=machine, args=(config2,))
    "[]"
    config3=[localHost, port3, port1]
    p3 = Process(target=machine, args=(config3,))

    p1.start()
    p2.start()
    p3.start()
    
    p1.join()
    p2.join()
    p3.join()