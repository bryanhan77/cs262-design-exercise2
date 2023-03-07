from multiprocessing import Process
import os
import socket
from _thread import *
import threading
import time
from threading import Thread
import random
from collections import deque
import csv
from datetime import datetime


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
        self.code = "msg0"

        self.logical_clock = 0

        self.server_socket = None
        self.client_socket = None


# each consumer is a server: constantly listening
def consumer(conn, ThisProcess):
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
        time.sleep(3)

        # start consumer thread for every consumer
        print("[CONSUMER TO SERVER] Connected to port: " + str(PORT) + "\n")
        start_new_thread(consumer, (conn, ThisProcess))
 

# individual machine process
def machine(config, id):
    config.append(os.getpid())
    # config: [address, server port, client port, process id]
    # need a clockrate between 1-6 (# of instructions per second)
    ThisProcess = MachineProcess(config)
    # ThisProcess.clockrate = 6

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
        time.sleep(5)
        # bidirectional stream
        start_new_thread(consumer, (client, ThisProcess))

        print("[SERVER TO CONSUMER] Connected to port: " + str(PORT) + "\n")
        ThisProcess.client_socket = client

    except socket.error as e:
        print("Error connecting producer: %s" % e)

    # initialize file to write to
    filename = 'log' + str(ThisProcess.config["process_id"]) + '.csv'
    with open(filename, 'w', newline='', encoding=FORMAT) as csvfile:
        # receive operation, the global time (gotten from the system), the length of the message queue, and the logical clock time.
        fieldnames = ['operation', '\t\t\t\tglobal_time', 
                      '\t\tlength_of_queue', '\tlogical_clock', '\torigin server',
                      '\t\tclockrate: ' + str(ThisProcess.clockrate), 
                      '\tServer port: ' + str(ThisProcess.config['server_port']), 
                      '\tClient port: ' + str(ThisProcess.config['client_port'])]
        # writer = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer = csv.writer(csvfile, delimiter=' ', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fieldnames)
    
    # machine loop to process clock cycles
    # TODO: open a file to print out all the history
    while True:
        # append to log
        with open(filename, 'a', newline='', encoding=FORMAT) as csvfile:
            begin = time.process_time()

            # receive operation, the global time (gotten from the system), the length of the message queue, and the logical clock time.
            writer = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)

            # TODO: these happen clockrate times all in a fraction of a second
            for _ in range(ThisProcess.clockrate):
                ThisProcess.code = "msg" + str(random.randint(1,20))
                # if message in the queue, pop from msg_queue 
                if ThisProcess.msg_queue:
                    
                    print(str(ThisProcess.clockrate) + ". " + str(ThisProcess.msg_queue))
                    message = ThisProcess.msg_queue.popleft().split("~")
                    
                    # update logical clock
                    ThisProcess.logical_clock = max(ThisProcess.logical_clock, int(message[0])) + 1

                    # write to log
                    current_time = datetime.now()
                    writer.writerow(['receive\t\t', '' + str(current_time), 
                                    '\t' + str(len(ThisProcess.msg_queue)) + '\t\t', 
                                    str(ThisProcess.logical_clock), 
                                    message[1]])

                # TODO: if message queue is empty, generate message
                else:
                    # 1) send message
                    # codeVal = str(ThisProcess.logical_clock) + "~" + str(ThisProcess.code)
                    codeVal = str(ThisProcess.logical_clock) + "~" + str(ThisProcess.config['server_port'])
                    message_body = codeVal.encode(FORMAT)
                    message_length = len(message_body).to_bytes(1, BYTE_ORDER)

                    # 1: send to server. 2: send to client. 3: send to both. 4-6: internal event. 
                    operation = random.randint(1, 10)
                    if 1 <= operation <= 3:
                        if operation == 1:
                            ThisProcess.server_socket.send(message_length + message_body)
                        elif operation == 2:
                            ThisProcess.client_socket.send(message_length + message_body)
                        elif operation == 3:
                            ThisProcess.server_socket.send(message_length + message_body)
                            ThisProcess.client_socket.send(message_length + message_body)
                    else:
                        # internal event
                        pass
                    
                    # 2) update logical clock
                    ThisProcess.logical_clock += 1

                    # 3) update log with send
                    event_type = "send\t\t\t" if operation <= 3 else "internal event\t"
                    current_time = datetime.now()
                    writer.writerow([event_type, '' + str(current_time),
                                    '\t' + str(len(ThisProcess.msg_queue)) + '\t\t',
                                    str(ThisProcess.logical_clock)])
                    
                    print(str(ThisProcess.clockrate) + ". msg sent", codeVal)

            # sleep for the remainder of the second
            end = time.process_time()
            time.sleep(1 - (end - begin))


    
if __name__ == '__main__':

    localHost= "127.0.0.1"
    port1 = 18001
    port2 = 28001
    port3 = 38001
    
    # 1 connects to 2 and receives from 3
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