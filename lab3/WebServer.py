#This file is created by using Python3.7

import socket
import sys
#(i) create a connection socket when contacted by a client (browser).

#(ii) receive HTTP request from this connection. Your server should only process GET request. You may assume that only GET requests will be received.

#(iii) parse the request to determine the specific file being requested.

#(iv) get the requested file from the server's file system.

#(v) create an HTTP response message consisting of the requested file preceded by header lines.

#(vi) send the response over the TCP connection to the requesting browser.

#(vii) If the requested file is not present on the server, the server should send an HTTP 404 Not Found message back to the client.

#(viii) the server should listen in a loop, waiting for next request from the browser.

def main():
    #Check the command line
    if len(sys.argv) != 2:
        print("Required arguments: port")
        return
    #read the port from command line and convert to int type
    port = int(sys.argv[1])
    #create a serversocket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #connect the socket with the port
    serverSocket.bind(('', port))
    #set the socket to listening mode and set the maximum number of queued connections to be 1 so it handle one request at a time
    serverSocket.listen(1)
    #Processing loop
    while True:
        #create connection socket
        connection, address = serverSocket.accept()
        try:
            #receive HTTP request from this connection(only GET)
            buf = connection.recv(1024)
            #print(buf)

            # parse the request to determine the specific file being requested.
            request = buf.split();
            #print(message)

            file = request[1]
            #print (file)

            name = file.replace('/', '')
            #print (file_name)

            #get the requested file from the server's file system.
            file = open(name)
            output = file.read()
            #create an HTTP response message consisting of the requested file preceded by header lines.
            #send the response over the TCP connection to the requesting browser
            connection.send('HTTP/1.1 200 OK\n\n')
            connection.send(output)
            connection.close()
        # send an HTTP 404 Not Found message back to the client if the requested file is not present on the server
        except:
            connection.send('HTTP/1.1 404 File not found\n\n')
            connection.send('<h1>404 Error: File not found</h1>')
            connection.close()
main()
