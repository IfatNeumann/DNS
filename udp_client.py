from socket import socket, AF_INET, SOCK_DGRAM
import sys
import time
import ast

def findInCache(key):
    if not (key in cache):
        return False
    if len(cache[key])<2:
        return False
    timeStamp = cache[key][4]
    ttl = cache[key][3]
    if timeStamp != '-1' and (time.clock() - float(timeStamp) > float(ttl) ):
        del cache[key]
        return False
    return  True

s = socket(AF_INET, SOCK_DGRAM)
#server's info
dest_ip = sys.argv[1]
dest_port = int(sys.argv[2])

# create cache for the client
cache = {}

msg = raw_input("Message to send: ")
while not msg == 'quit':
    key = msg.split(',')[0][1:]
    if findInCache(key):
        print "You have in cache: "+str(cache[key])
    else:
        s.sendto(msg, (dest_ip,dest_port))
        data, _ = s.recvfrom(2048)
        print "Server sent: ", data

        # add to cache
        key = data[1:-1].split(',')[0][1:-1]
        data = ast.literal_eval(data)
        data[4] = time.clock()
        cache[key] = data
    msg = raw_input("Message to send: ")
s.close()