from socket import socket, AF_INET, SOCK_DGRAM

s = socket(AF_INET, SOCK_DGRAM)
dest_ip = '127.0.0.1'
dest_port = 12345
msg = raw_input("Message to send: ")
while not msg == 'quit':
    s.sendto(msg, (dest_ip,dest_port))
    data, _ = s.recvfrom(2048)
    print "Server sent: ", data
    msg = raw_input("Message to send: ")
s.close()