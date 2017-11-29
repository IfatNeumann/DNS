from socket import socket, AF_INET, SOCK_DGRAM
import sys
import time

# initialize resolver
resolver = False
if str(sys.argv[1]) == "resolver":
    resolver = True

s = socket(AF_INET, SOCK_DGRAM)
source_ip = '0.0.0.0'
source_port = 12345

# save mapping's data in a dictionary
mappingFile=open("mapping.txt","r")
mappingDict = {}
for line in mappingFile:
    l = line.split()
    mappingDict[l[0]] = l

s.bind((source_ip, source_port))
while True:
    data, sender_info = s.recvfrom(2048)
    print "Message: ", data, " from: ", sender_info, time.clock()
    #s.sendto(data.upper(), sender_info)
    #search in dict
    key = data.split(',')[0][1:]
    if key in mappingDict:
        msg = mappingDict[key][2]
        s.sendto(msg, sender_info)
    #else:
        #if resolver:
     #   s.sendto(msg, (source_ip, source_port))