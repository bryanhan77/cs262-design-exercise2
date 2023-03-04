from multiprocessing import Process
import os
import socket
from _thread import *
import threading
import time
from threading import Thread
import random
from collections import deque

FORMAT = 'ascii'
BYTE_ORDER = 'big'

class MachineProcess():
    def __init__(self, config):
        self.config = {
            "address": config[0],
            "server_port": config[1],
            "client_port": config[2],
            "process_id": config[3]
        }
        self.msg_queue = deque()
        self.clockrate = random.randint(1,6)
        # self.code = "message"

        self.logical_clock = 0

        self.server_socket = None
        self.client_socket = None


# each consumer is a server: constantly listening
def consumer(conn, ThisProcess):
    print("[CONSUMER] new thread for client " + str(conn) + "\n")

    # should be different for every machine
    while True:
        message_len = conn.recv(1)
        message_len = int.from_bytes(message_len, byteorder=BYTE_ORDER)

        data = conn.recv(message_len)
        dataVal = data.decode(FORMAT)

        ThisProcess.msg_queue.append(dataVal)
 

# initialize listening server for each machine: constantly listening
def init_machine(ThisProcess):
    # config: [address, listening port, connected port, process id]
    ADDR, PORT = str(ThisProcess.config["address"]), int(ThisProcess.config["server_port"])
    PID = str(ThisProcess.config["process_id"])
    
    print("[INIT MACHINE] Listening on port: " + str(PORT) + " for process: " + PID + "\n")
    print("clockrate: " + str(ThisProcess.clockrate) + "\n")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ADDR, PORT))
    server.listen()

    while True:
        conn, addr = server.accept()

        ThisProcess.server_socket = conn
        # start consumer thread for every consumer
        start_new_thread(consumer, (conn, ThisProcess))
 

# individual machine process
def machine(config, id):
    config.append(os.getpid())
    # config: [address, server port, client port, process id]
    # need a clockrate between 1-6 (# of instructions per second)
    ThisProcess = MachineProcess(config)
    ThisProcess.clockrate = id

    # randomized message
    global code
    
    print("[MACHINE] config: " + str(config) + "\n")
    
    # thread for listening
    init_thread = Thread(target=init_machine, args=(ThisProcess,))
    init_thread.start()
    #add delay to initialize the server-side logic on all processes
    time.sleep(5)

    # must produce within the main while loop
    ADDR, PORT = str(ThisProcess.config['address']), int(ThisProcess.config["client_port"])
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        client.connect((ADDR, PORT))
        print("[PRODUCER] Connected to port: " + str(PORT) + "\n")
        ThisProcess.client_socket = client
    except socket.error as e:
        print("Error connecting producer: %s" % e)

    # machine loop to process clock cycles
    # TODO: open a file to print out all the history
    while True:
        
        begin = time.process_time()

        # TODO: these happen clockrate times all in a fraction of a second
        for _ in range(ThisProcess.clockrate):
            code = random.randint(1,3)
            # TODO: if message in the queue, pop from msg_queue 
            if ThisProcess.msg_queue:
                print(str(ThisProcess.clockrate) + ". " + str(ThisProcess.msg_queue))
                
                message = ThisProcess.msg_queue.popleft().split("~")
                # update logical clock
                ThisProcess.logical_clock = max(ThisProcess.logical_clock, int(message[0])) + 1

            # TODO: if message queue is empty, generate message
            else:
                ThisProcess.logical_clock += 1
                codeVal = str(ThisProcess.logical_clock) + "~" + str(code)

                message_body = codeVal.encode(FORMAT)
                message_length = len(message_body).to_bytes(1, BYTE_ORDER)

                client.send(message_length + message_body)

                print(str(ThisProcess.clockrate) + ". msg sent", codeVal)


        end = time.process_time()
        print(str(ThisProcess.clockrate) + ". Time Elapsed: " + str(end - begin) + "\n")


        # sleep for the remainder of the second
        time.sleep(1 - (end - begin))
        


    
if __name__ == '__main__':

    localHost= "127.0.0.1"
    port1 = 18001
    port2 = 28001
    port3 = 38001
    
    config1=[localHost, port1, port2]
    p1 = Process(target=machine, args=(config1, 1))

    config2=[localHost, port2, port3]
    p2 = Process(target=machine, args=(config2, 3))

    config3=[localHost, port3, port1]
    p3 = Process(target=machine, args=(config3, 6))

    p1.start()
    p2.start()
    p3.start()
    
    p1.join()
    p2.join()
    p3.join()