from socket import socket, AF_INET, SOCK_DGRAM
import sys

s = socket(AF_INET, SOCK_DGRAM)
#server's info
dest_ip = '127.0.0.1'
dest_port = int(str(sys.argv[1]))

msg = raw_input("Message to send: ")
while not msg == 'quit':
    s.sendto(msg, (dest_ip,dest_port))
    data, _ = s.recvfrom(2048)
    print "Server sent: ", data
    msg = raw_input("Message to send: ")
s.close()