
from socket import *
import threading
import time
import sys



t_lock=threading.Condition()
#will store clients info in this list
clients=[]
#store the successor in this list
successor=[]

#read the most important args
type = sys.argv[1]
#for init, read args and record the successor
if(type == "init"):
    peerID = int(sys.argv[2])
    first_successor = int(sys.argv[3])
    second_successor = int(sys.argv[4])
    ping_interval = float(sys.argv[5])
    #record the successor of this peer
    successor.append(first_successor)
    successor.append(second_successor)
#for join, send the join request to the known peer through TCP
elif(type == "join"):
    peerID = int(sys.argv[2])
    known_peer = int(sys.argv[3])
    ping_interval = float(sys.argv[4])
    TCPPort = 18000 + known_peer
    #message1 = "prepare for join"
    message1 = "join "+str(peerID)
    TCPClient = socket(AF_INET, SOCK_STREAM)
    TCPClient.connect(('localhost', TCPPort))
    TCPClient.send(message1.encode())
    print("Join request send to Peer" + str(known_peer))
    TCPClient.close()
    sys.exit()
else:
    print("No such type")
    sys.exit()

#Server will run on this port
serverPort = 12000 + peerID
# would communicate with clients after every second
UPDATE_INTERVAL= ping_interval
timeout=False

#The basic structure of this thread is come from the sample server file in WebCMS3!
def recv_handler():
    global t_lock
    global clients
    global clientSocket
    global serverSocket
    global successor
    print('Server is ready for service')
    while(1):

        message, clientAddress = serverSocket.recvfrom(2048)
        #received data from the client, now we know who we are talking with
        message = message.decode()
        #get lock as we might me accessing some shared data structures
        with t_lock:
            temp = message.split(" ")
            if(temp[0] == 'Subscribe'):
                print("Ping request received from Peer" + temp[1])
                #store client information (IP and Port No) in list
                clients.append(clientAddress)
                serverMessage="Ping response received from Peer "+str(peerID)#"Subscription successfull"
            elif(message=='Unsubscribe'):
                #check if client already subscribed or not
                if(clientAddress in clients):
                    clients.remove(clientAddress)
                    serverMessage="Subscription removed"
                else:
                    serverMessage="You are not currently subscribed"
            else:
                serverMessage="Unknown command, send Subscribe or Unsubscribe only"
            #send message to the client
            serverSocket.sendto(serverMessage.encode(), clientAddress)
            #notify the thread waiting
            t_lock.notify()
        receivedMessage, serverAddress = clientSocket.recvfrom(2048)
        print(receivedMessage.decode())
#The basic structure of this thread is come from the sample server file in WebCMS3!
def send_handler():
    global t_lock
    global clients
    global clientSocket
    global serverSocket
    global timeout
    global successor
    #go through the list of the subscribed clients and send them the current time after every 1 second
    while(1):
        #get lock
        with t_lock:
            if(type == "init"):
                serverName = 'localhost'
                FserverPort = 12000 + successor[0]
                SserverPort = 12000 + successor[1]
                #message = "Ping request message received from peer " + str(peerID)
                message = 'Subscribe'+' '+str(peerID)
                clientSocket.sendto(message.encode(), (serverName,FserverPort))
                clientSocket.sendto(message.encode(), (serverName,SserverPort))
                print("Ping requests were sent to Peer", successor[0], "and ", successor[1])

            for i in clients:
                message = "Ping response received from Peer "+str(peerID)
                clientSocket.sendto(message.encode(), i)
            #notify other thread
            t_lock.notify()
        #sleep for UPDATE_INTERVAL
        time.sleep(UPDATE_INTERVAL)

def TCP_handler():
    global t_lock
    global clients
    global clientSocket
    global serverSocket
    global successor

    while(1):
        connectionSocket, addr = TCPserverSocket.accept()
        #received data from the client, now we know who we are talking with
        sentence = connectionSocket.recv(1024)
        sentence.decode()
        #get lock as we might me accessing some shared data structures
        with t_lock:
            temp = sentence.split(" ")
            #deal with join command
            if(temp[0]=='join'):
                print("join")
                JpeerID = int(temp[1])
                #eg 1 3 5
                if(peerID < successor[0] and peerID < successor[1]):
                    #eg 6
                    if(JpeerID > successor[1]):
                        message = sentence
                        TCPClient = socket(AF_INET, SOCK_STREAM)
                        TCPPort = 18000 + successor[0]
                        TCPClient.connect(('localhost', TCPPort))
                        TCPClient.send(message.encode())
                        print("Peer " + temp[1] + " Join request forwarded to my successor")
                        TCPClient.close()
                    #eg 4
                    elif(JpeerID > successor[0] and JpeerID < successor[1]):
                        #unsubscribe the 2nd successor
                        message='Unsubscribe'
                        SserverPort = 12000 + successor[1]
                        clientSocket.sendto(message.encode(), ('localhost',SserverPort))
                        #remove the 2nd successor
                        successor.remove(successor[1])
                        #make the joined peer as second successor
                        successor.append(JpeerID)
                        print("My new first successor is Peer "+str(successor[0]))
                        print("My new second successor is Peer "+str(successor[1]))
                        #forward the join request to 1st successor
                        message = sentence
                        TCPClient = socket(AF_INET, SOCK_STREAM)
                        TCPPort = 18000 + successor[0]
                        TCPClient.connect(('localhost', TCPPort))
                        TCPClient.send(message.encode())
                        print("Peer " + temp[1] + " Join request forwarded to my successor")
                        TCPClient.close()
                    #eg 2
                    elif(JpeerID<successor[0] and JpeerID>peerID):
                        cmd1 = 'xterm -hold -title "Peer 1" -e'
                        cmd11 = cmd1.replace('1',str(JpeerID))
                        cmd2 = ' python p2p.py init '+str(JpeerID)+" "+str(successor[0])+" "+str(successor[1])+" 30"
                        ##init the joined peer
                        #cmd = "python p2p.py init " + str(JpeerID) + " " + str(successor[0]) + " " + str(successor[1]) + " 30"
                        #jpeer = "Peer "+ str(JpeerID) +" "
                        #os.system('xterm -hold -title '+ jpeer +' -e'+cmd)

                        #unsubscribe the 2nd successor
                        message='Unsubscribe'
                        SserverPort = 12000 + successor[1]
                        clientSocket.sendto(message.encode(), ('localhost',SserverPort))
                        #remove the 2nd successor
                        successor.remove(successor[1])
                        #make the joined successor as 1st successr and 1st successor as 2nd successor
                        successor.insert(0,JpeerID)

                        print("Peer "+temp[1] +" Join request received")
                        print("My new first successor is Peer "+str(successor[0]))
                        print("My new second successor is Peer "+str(successor[1]))

                        print("Please input")
                        print(cmd11+cmd2)
                    #JpeerID < peerID
                    else:
                        message = sentence
                        TCPClient = socket(AF_INET, SOCK_STREAM)
                        TCPPort = 18000 + successor[0]
                        TCPClient.connect(('localhost', TCPPort))
                        TCPClient.send(message.encode())
                        print("Peer " + temp[1] + " Join request forwarded to my successor")
                        TCPClient.close()
                #eg. 9 13 1
                elif(peerID < successor[0] and peerID > successor[1]):
                    #eg 2
                    if(JpeerID<successor[0] and JpeerID > successor[1]):
                        message = sentence
                        TCPClient = socket(AF_INET, SOCK_STREAM)
                        TCPPort = 18000 + successor[0]
                        TCPClient.connect(('localhost', TCPPort))
                        TCPClient.send(message.encode())
                        print("Peer " + temp[1] + " Join request forwarded to my successor")
                        TCPClient.close()
                    #eg 14
                    elif(JpeerID > successor[0] and JpeerID > successor[1]):

                        #unsubscribe the 2nd successor
                        message='Unsubscribe'
                        SserverPort = 12000 + successor[1]
                        clientSocket.sendto(message.encode(), ('localhost',SserverPort))
                        #remove the 2nd successor
                        successor.remove(successor[1])
                        #make the joined peer as second successor
                        successor.append(JpeerID)
                        print("My new first successor is Peer "+str(successor[0]))
                        print("My new second successor is Peer "+str(successor[1]))
                        #forward the join request to 1st successor
                        message = sentence
                        TCPClient = socket(AF_INET, SOCK_STREAM)
                        TCPPort = 18000 + successor[0]
                        TCPClient.connect(('localhost', TCPPort))
                        TCPClient.send(message.encode())
                        print("Peer " + temp[1] + " Join request forwarded to my successor")
                        TCPClient.close()
                        #os.system(cmd1+cmd2)

                    #eg 12
                    elif(JpeerID<successor[0] and JpeerID>peerID):
                        cmd1 = 'xterm -hold -title "Peer 1" -e'
                        cmd11 = cmd1.replace('1',str(JpeerID))
                        cmd2 = ' python p2p.py init '+str(JpeerID)+" "+str(successor[0])+" "+str(successor[1])+" 30"

                        #unsubscribe the 2nd successor
                        message='Unsubscribe'
                        SserverPort = 12000 + successor[1]
                        clientSocket.sendto(message.encode(), ('localhost',SserverPort))
                        #remove the 2nd successor
                        successor.remove(successor[1])
                        #make the joined successor as 1st successr and 1st successor as 2nd successor
                        successor.insert(0,JpeerID)

                        print("Peer "+temp[1] +" Join request received")
                        print("My new first successor is Peer "+str(successor[0]))
                        print("My new second successor is Peer "+str(successor[1]))

                        print("Please input")
                        print(cmd11+cmd2)
                    #JpeerID < peerID
                    else:
                        message = sentence
                        TCPClient = socket(AF_INET, SOCK_STREAM)
                        TCPPort = 18000 + successor[0]
                        TCPClient.connect(('localhost', TCPPort))
                        TCPClient.send(message.encode())
                        print("Peer " + temp[1] + " Join request forwarded to my successor")
                        TCPClient.close()
                #eg. 13 1 4
                elif(peerID > successor[0] and peerID > successor[1]):
                    #eg 5
                    if(JpeerID<peerID and JpeerID > successor[1]):
                        message = sentence
                        TCPClient = socket(AF_INET, SOCK_STREAM)
                        TCPPort = 18000 + successor[0]
                        TCPClient.connect(('localhost', TCPPort))
                        TCPClient.send(message.encode())
                        print("Peer " + temp[1] + " Join request forwarded to my successor")
                        TCPClient.close()
                    #eg 3
                    elif(JpeerID > successor[0] and JpeerID < successor[1]):
                        #unsubscribe the 2nd successor
                        message='Unsubscribe'
                        SserverPort = 12000 + successor[1]
                        clientSocket.sendto(message.encode(), ('localhost',SserverPort))
                        #remove the 2nd successor
                        successor.remove(successor[1])
                        #make the joined peer as second successor
                        successor.append(JpeerID)
                        print("My new first successor is Peer "+str(successor[0]))
                        print("My new second successor is Peer "+str(successor[1]))
                        ##forward the join request to 1st successor
                        message = sentence
                        TCPClient = socket(AF_INET, SOCK_STREAM)
                        TCPPort = 18000 + successor[0]
                        TCPClient.connect(('localhost', TCPPort))
                        TCPClient.send(message.encode())
                        print("Peer " + temp[1] + " Join request forwarded to my successor")
                        TCPClient.close()
                    #eg 14
                    elif(JpeerID>peerID):
                        cmd1 = 'xterm -hold -title "Peer 1" -e'
                        cmd11 = cmd1.replace('1',str(JpeerID))
                        cmd2 = ' python p2p.py init '+str(JpeerID)+" "+str(successor[0])+" "+str(successor[1])+" 30"
                        #unsubscribe the 2nd successor
                        message='Unsubscribe'
                        SserverPort = 12000 + successor[1]
                        clientSocket.sendto(message.encode(), ('localhost',SserverPort))
                        #remove the 2nd successor
                        successor.remove(successor[1])
                        #make the joined successor as 1st successr and 1st successor as 2nd successor
                        successor.insert(0,JpeerID)

                        print("Peer "+temp[1] +" Join request received")
                        print("My new first successor is Peer "+str(successor[0]))
                        print("My new second successor is Peer "+str(successor[1]))
                        print("Please input")
                        print(cmd11+cmd2)
                    #JpeerID < peerID
                    else:
                        message = sentence
                        TCPClient = socket(AF_INET, SOCK_STREAM)
                        TCPPort = 18000 + successor[0]
                        TCPClient.connect(('localhost', TCPPort))
                        TCPClient.send(message.encode())
                        print("Peer " + temp[1] + " Join request forwarded to my successor")
                        TCPClient.close()
            #deal with quit command
            elif(temp[0]=="Quit"):
                #if the Quit peer is the second successor
                if(successor[1] == int(temp[1])):
                    #forward the quit message to next successor
                    message=sentence
                    TCPClient = socket(AF_INET, SOCK_STREAM)
                    TCPPort = 18000 + successor[0]
                    TCPClient.connect(('localhost', TCPPort))
                    TCPClient.send(message.encode())
                    print("Quit request forwarded to my successor")
                    TCPClient.close()
                    #print the update successor
                    print("Peer "+str(successor[1])+"will depart from the network")
                    second_successor = int(temp[2])
                    print("My new first successor is Peer "+str(successor[0]))
                    print("My new second successor is Peer "+str(second_successor))
                    #unsubscirbe original 2nd successor
                    message='Unsubscribe'
                    SserverPort = 12000 + successor[1]
                    clientSocket.sendto(message.encode(), ('localhost',SserverPort))
                    #update the successor list
                    successor.remove(successor[1])
                    successor.append(second_successor)
                #if the Quit peer is the next successor
                elif(successor[0] == int(temp[1])):
                    print("Peer "+str(successor[0])+"will depart from the network")
                    first_successor = int(temp[2])
                    second_successor = int(temp[3])
                    #print the new successor message
                    print("My new first successor is Peer "+str(first_successor))
                    print("My new second successor is Peer "+str(second_successor))
                    #unsubscribe the original successor
                    message='Unsubscribe'
                    FserverPort = 12000 + successor[0]
                    SserverPort = 12000 + successor[1]
                    clientSocket.sendto(message.encode(), ('localhost',FserverPort))
                    clientSocket.sendto(message.encode(), ('localhost',SserverPort))
                    #update the successor list
                    successor=[]
                    successor.append(first_successor)
                    successor.append(second_successor)
                #if the Quit peer is not the next successor
                else:
                    #forward the quit message to next successor
                    message=sentence
                    TCPClient = socket(AF_INET, SOCK_STREAM)
                    TCPPort = 18000 + successor[0]
                    TCPClient.connect(('localhost', TCPPort))
                    TCPClient.send(message.encode())
                    print("Quit request forwarded to my successor")
                    TCPClient.close()
            #deal with store command
            elif(temp[0]== 'Store'):
                #the store request is accepted
                filename = temp[1]
                Sfilename = (int(filename)%256)
                if(Sfilename == peerID):
                    print(sentence + ' request accepted')
                else:
                    #forward the quit message to next successor
                    TCPClient = socket(AF_INET, SOCK_STREAM)
                    TCPPort = 18000 + successor[0]
                    TCPClient.connect(('localhost', TCPPort))
                    TCPClient.send(sentence.encode())
                    print(sentence + " request forwarded to my successor")
                    TCPClient.close()
                    #print('stored')
            #deal with the request command
            elif(temp[0]=='Request'):
                #print('Requested')
                #the request request is accepted
                filename = temp[1]
                Sfilename = (int(filename)%256)
                if(Sfilename == peerID):
                    print('File' + temp[1] + ' is stored here')
                    print('Start sending file '+temp[1]+' to peer '+temp[2])
                    #get the file name and port number of destination
                    TCPPort = 18000+int(temp[2])
                    #ask the destination to be prepared
                    message = 'Prepare' + ' '+filename
                    TCPClient = socket(AF_INET, SOCK_STREAM)
                    TCPClient.connect(('localhost', TCPPort))
                    TCPClient.send(message.encode())

                    #try to check the exitence of the file
                    try:
                        test = open(filename, "rb")
                        #send the file to destination
                        data = test.read()
                        TCPClient.sendall(data)
                        # close connection
                        TCPClient.close()
                        print("The file has been sent")
                    except IOError:
                        print("no such file")
                else:
                    #forward the quit message to next successor
                    TCPClient = socket(AF_INET, SOCK_STREAM)
                    TCPPort = 18000 + successor[0]
                    TCPClient.connect(('localhost', TCPPort))
                    TCPClient.send(sentence.encode())
                    print(temp[0] +' '+temp[1] + " request has been received, but the file is not stored here")
                    TCPClient.close()
            #prepare to receive file
            elif(temp[0]=='Prepare'):

                receive = open("received_"+temp[1],"wb")
                while(True):
                    data = connectionSocket.recv(4096)
                    if(not data):
                        break
                    receive.write(data)
                receive.close()
                print('File received')

            #close connection
            connectionSocket.close()
            #notify the thread waiting
            t_lock.notify()
        #receivedMessage, serverAddress = clientSocket.recvfrom(2048)
        #print(receivedMessage.decode())

def Input_handler():
    global t_lock
    global clients
    global clientSocket
    global serverSocket
    global successor
    global TCPserverSocket

    while(1):
        Imessage = input()
        temp = Imessage.split(' ')
        #get lock
        with t_lock:
            #print(Imessage+" is got")
            if(Imessage == 'Quit'):
                #print(Imessage+" is got")
                #unsubscibe the successors
                message='Unsubscribe'
                FserverPort = 12000 + successor[0]
                SserverPort = 12000 + successor[1]
                clientSocket.sendto(message.encode(), ('localhost',FserverPort))
                clientSocket.sendto(message.encode(), ('localhost',SserverPort))
                #send quit message to successor through TCP
                message2='Quit '+str(peerID)+' '+str(successor[0]) + ' '+str(successor[1])
                TCPClient = socket(AF_INET, SOCK_STREAM)
                TCPPort = 18000 + successor[0]
                TCPClient.connect(('localhost', TCPPort))
                TCPClient.send(message2.encode())
                print("Quit request forwarded to my successor")
                TCPClient.close()
                #clear the successor list
                successor=[]
                clientSocket.close()
                serverSocket.close()
                TCPserverSocket.close()
                print('All socket closed, please close the terminal')
            elif(temp[0]== 'Store'):
                #the store request is accepted
                filename = temp[1]
                Sfilename = (int(filename)%256)
                if(Sfilename == peerID):
                    print(Imessage + ' request accepted')
                else:
                    #forward the quit message to next successor
                    TCPClient = socket(AF_INET, SOCK_STREAM)
                    TCPPort = 18000 + successor[0]
                    TCPClient.connect(('localhost', TCPPort))
                    TCPClient.send(Imessage.encode())
                    print(Imessage + " request forwarded to my successor")
                    TCPClient.close()
                        #print('stored')
            elif(temp[0]=='Request'):
                #print('Requested')
                #the request request is accepted
                filename = temp[1]
                Sfilename = (int(filename)%256)
                if(Sfilename == peerID):
                    print(Imessage + ' is stored here')
                    print('No transmission required')
                else:
                    Rmessage = Imessage +' '+str(peerID)
                    #forward the quit message to next successor
                    TCPClient = socket(AF_INET, SOCK_STREAM)
                    TCPPort = 18000 + successor[0]
                    TCPClient.connect(('localhost', TCPPort))
                    TCPClient.send(Rmessage.encode())
                    print(Imessage + " request has been sent to my successor")
                    TCPClient.close()
            else:
                print('no such command')
            #notify the thread waiting
            t_lock.notify()

#The basic structure of following code is come from the sample server file in WebCMS3!
#we will use two sockets, one for sending and one for receiving
clientSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('localhost', serverPort))

TCPserverSocket = socket(AF_INET, SOCK_STREAM)
TCPPort = 18000 + peerID
TCPserverSocket.bind(('localhost', TCPPort))
TCPserverSocket.listen(1)

recv_thread=threading.Thread(name="RecvHandler", target=recv_handler)
recv_thread.daemon=True
recv_thread.start()

send_thread=threading.Thread(name="SendHandler",target=send_handler)
send_thread.daemon=True
send_thread.start()
#this is the main thread

tcp_thread=threading.Thread(name="TCPHandler",target=TCP_handler)
tcp_thread.daemon=True
tcp_thread.start()

input_thread=threading.Thread(name="InputHandler",target=Input_handler)
input_thread.daemon=True
input_thread.start()
while True:
    try:
        time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        print('Peer '+str(peerID)+' is killed')
        message='Unsubscribe'
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        FserverPort = 12000 + successor[0]
        SserverPort = 12000 + successor[1]
        clientSocket.sendto(message.encode(), ('localhost',FserverPort))
        clientSocket.sendto(message.encode(), ('localhost',SserverPort))
        #send quit message to successor through TCP
        message2='Quit '+str(peerID)+' '+str(successor[0]) + ' '+str(successor[1])
        TCPClient = socket(AF_INET, SOCK_STREAM)
        TCPPort = 18000 + successor[0]
        TCPClient.connect(('localhost', TCPPort))
        TCPClient.send(message2.encode())
        print("Quit request forwarded to my successor")
        TCPClient.close()
#try:
#    start_thread()
#except (KeyboardInterrupt, SystemExit):
#    cleanup_stop_thread()
#    sys.exit()