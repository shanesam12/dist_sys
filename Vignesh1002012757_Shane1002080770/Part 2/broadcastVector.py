#CSE 5306 - 004 Distributed Systems
#Project 2
#Vignesh Manikandan - 1002012757
#Shane Sam Antony Rebinto Sam - 1002080770
#Part 2 Broadcast message

import sys
import threading
import socket
import time 
import random
import pickle

EventList = {}
proId = 0

def vector_max(vector1,vector2):
    #To get the maximum value
    vector = [max(value) for value in zip(vector1,vector2)]
    return vector

def handler(conn,add):
    # Check Flag and determine vector clocks
    print(f"\n[+] {add} is connected.")
    received = conn
    if received:
        print(f"Vector clock for all events before receiving:{EventList}\n")
        data = pickle.loads(received)
        print("/n")

        for rEventId in EventList:
            if rEventId != data["sEventId"]:
                vector = vector_max(data["sEventData"] , EventList[rEventId])
                EventList[rEventId] = vector
                print(f"New Vector Value For Event:{rEventId} is {vector}")
                print("\n")
            
                if (rEventId + 1) in EventList:
                    for i in range(rEventId + 1, len(EventList) + 1):
                        EventList[i] = vector_max(EventList[i-1],EventList[i])
      
        received = None      

def listen(node):
    while True:
        conn,addr = node.recvfrom(1024)
        print(f"\nReceiving Message from:{addr}")
        print("\n")
        if conn and addr:
            thread = threading.Thread(target=handler,args=(conn,addr))
            thread.start()



def sender():
    while True:
        option = int(input("1. Enter 1 to Communicate\n2. Enter 2 to Skip\n3. Enter 3 to Exit\n Enter your choice:"))
        print("\n")
        if option == 1:
            print(f"Vector clock for all events before sending:{EventList}\n")
            recieverPort = int(input("Enter port number of receiver: "))
            print("\n")
            if recieverPort:
                messagedata = {}
                
                sEventId = int(input("Enter Sender Event Number:"))
                print("\n")
                EventList[sEventId][proId-1] += 1
                sEventData = EventList[sEventId]
                print("\n")

                messagedata["sEventId"] = sEventId
                messagedata["sEventData"] = sEventData
                data = pickle.dumps(messagedata)
                try:
                    print(f"\nBroadcasting Message to 127.0.0.1:{recieverPort}\n")
                    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
                    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    conn.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #setting to broadcast mode
                    conn.connect(('localhost',recieverPort))
                    broadcast_address = ('<broadcast>', recieverPort)
                    print(f"\n[+] Connected and sending\n")

                    conn.sendto(data,broadcast_address)
                    time.sleep(5)
                    conn.close()
                    print(f"Vector clock for all events after sending:{EventList}\n")
                except Exception as e:
                    print(e)
                finally:
                    recieverPort = None
        elif option == 2:
            print("\n")
        else:
            print("Current Vector Clock for all Events\n")
            print(EventList)
            sys.exit()


def main(port):
    node = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    node.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    node.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #setting to broadcast mode

    node.bind(('',port))

    listener_thread = threading.Thread(target=listen,args=(node,))
    sender_thread = threading.Thread(target=sender,args=())
    listener_thread.start()
    sender_thread.start()

    


if __name__ == '__main__':
    port = int(input("Enter port number for the node:"))
    print("\n")
    pId = int(input("Process Id for the node(1/2/3):"))
    print("\n")
    proId = pId

    n1 = int(input(f"Enter the no. of events in Process {pId} : "))
    print("\n")
    e1 = [i for i in range(1, n1 + 1)]
    if pId == 1:
        EventList = {key: [key, 0, 0] for key in e1}
    elif pId == 2:
        EventList = {key: [0, key, 0] for key in e1}
    elif pId == 3:
        EventList = {key: [0, 0, key] for key in e1}
    print(EventList)
    print("\n")

    main(port)