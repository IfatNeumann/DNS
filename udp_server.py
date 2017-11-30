from socket import socket, AF_INET, SOCK_DGRAM
import sys
import time
#local
def findInMapping(url):
    if key in mappingDict:
        return True
    else:
        return False

# initialize resolver
resolver = False
if str(sys.argv[2]) == "resolver":
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
# add root to the dictionary
mappingDict['root'] = str(sys.argv[1])

s.bind((source_ip, source_port))
while True:
    data, sender_info = s.recvfrom(2048)
    print "Message: ", data, " from: ", sender_info, time.clock()
    #s.sendto(data.upper(), sender_info)
    # search www.bob.com
    key = data.split(',')[0][1:]
    if findInMapping(key) == True:
        msg = mappingDict[key][2]
        s.sendto(msg, sender_info)
    else:
        #search bob.com -> com
        key = key[key.find('.') + 1:]
        while findInMapping(key) == False and key.find('.')!=-1: #search NS
            key = key[key.find('.')+1:]
        # search in other servers
        # if found = send message
        if findInMapping(key) == True:
            msg = mappingDict[key][2]
            s.sendto(msg, sender_info) #iterate or recursive
        #if not found - try root
        else:
            print mappingDict['root']
            s.sendto(data, ('127.0.0.1',int(mappingDict['root'])))
            print "hi"
    #if resolver:
    #   s.sendto(msg, (source_ip, source_port))


