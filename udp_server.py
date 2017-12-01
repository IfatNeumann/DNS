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
client = ""
s.bind((source_ip, source_port))
while True:
    data, sender_info = s.recvfrom(2048)
    print "Message: ", data, " from: ", sender_info, time.clock()
    dataCopy = data.split(',')
    print dataCopy[0]
    # if size = 2: quest, if size = 3: answer
    if len(data)==2:
        client = sender_info
    if len(data) == 4:
        # save in cache
        mappingDict[dataCopy[0]] = dataCopy
        #if it's tha answer - return to the client
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
            s.sendto(data, ('127.0.0.1',int(mappingDict['root'])))
    #if resolver:
    #   s.sendto(msg, (source_ip, source_port))


