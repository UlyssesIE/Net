import java.io.*;
import java.net.*;
import java.util.*;

/*
 * Client to process ping requests over UDP.
 * The client sends 10 ping requests to the server.
 * Each message contains a payload of data that includes the keyword PING, a sequence number, and a timestamp.
 * After sending each packet, the client waits up to one second to receive a reply.
 * If one second goes by without a reply from the server, then the client assumes that its packet or the server's reply packet has been lost in the network.
 */

public class PingClient {
    public static void main(String[] args) throws Exception {
        // Get command line argument.
        if (args.length != 2) {
            System.out.println("Required arguments: host port");
            return;
        }
        // host is the IP address of the computer the server is running on
        String host = args[0];
        InetAddress severAddress = InetAddress.getByName(host);
        //port is the port number it is listening to
        int port = Integer.parseInt(args[1]);

        // Create a datagram socket for receiving and sending UDP packets
        // through the host and port specified on the command line.
        DatagramSocket socket = new DatagramSocket();

        //Enable SO_TIMEOUT with 10000 millisecond
        socket.setSoTimeout(1000);

        // Create a datagram packet to hold incomming UDP packet.
        DatagramPacket request = new DatagramPacket(new byte[1024], 1024);

        //Create a list to collect the output
        List<Long> result = new ArrayList<Long>();

        //send 10 ping message sequentially
        for (int i = 0; i < 10; i++) {
            //start time
            long startTime = System.currentTimeMillis();

            //create the string PING sequence_number time CRLF to be sent
            String ping = "PING " + (i) + " " + startTime + "\r\n";

            // Send reply.
            //InetAddress clientHost = request.getAddress();
            //int clientPort = request.getPort();
            //byte[] buf = request.getData();
            //DatagramPacket reply = new DatagramPacket(buf, buf.length, clientHost, clientPort);
            //socket.send(reply);

            //send the string
            byte[] buf = ping.getBytes();
            DatagramPacket send = new DatagramPacket(buf, buf.length, severAddress, port);
            //System.out.println("Packet sent: "+ping);
            socket.send(send);

            //try to receive reply
            try {
                socket.receive(request);
            } catch (SocketTimeoutException t) {
                System.out.println("The packet is lost");
                continue;
            }
            //end time
            long endTime = System.currentTimeMillis();
            //calculate the total time in milliseconds
            long totalTime = endTime - startTime;

            //ping to 127.0.0.1, seq = 1, rtt = 120 ms
            //replace the 'rtt=120ms' in the above example with 'time out'.
            System.out.println("ping to " + host + ", seq = " + i + ", time out = " + totalTime + " ms");
            result.add(totalTime);
        }

        //report the minimum, maximum and the average RTTs of all packets received successfully at the end of your program's output.
        Collections.sort(result);
        double low = result.get(0);
        double high = result.get(result.size()-1);
        System.out.println("The minimum RTTs is " +low);
        System.out.println("The maximum RTTs is " +high);

        double total = 0;
        for (int i = 0; i < result.size(); i++){
            total = total + result.get(i);
        }
        
        double avg = total / (result.size());
        System.out.println("The average RTTs is " +avg);
    }
}


