from socket import socket, AF_INET, SOCK_DGRAM
import sys
import time
#local
def findInMapping(url):
    if url in mappingDict:
        return True
    else:
        return False

def findAnswerNotResolver(data,sender_info,s):
    dataCopy = data.split(',')
    print dataCopy[0]
    # search www.bob.com -> bob.com -> com
    key = data.split(',')[0][1:]
    while findInMapping(key) == False and key.find('.') != -1:  # search NS
        key = key[key.find('.') + 1:]
    # if found = send message
    if findInMapping(key) == True:
        msg = mappingDict[key]
    # if not found or got to the end of the url - send IDK
    else:
        msg = "IDK"
    s.sendto(msg, sender_info)

def findAnswerResolver(data,sender_info,s,source_ip,source_port):
    dataCopy = data.split(',')
    print dataCopy[0]
    # search www.bob.com -> bob.com -> com
    key = data.split(',')[0][1:]
    # if found the url = send to the client
    if findInMapping(key) == True:
        msg = mappingDict[key]
        s.sendto(msg, sender_info)

    while findInMapping(key) == False and key.find('.') != -1:  # search NS
        key = key[key.find('.') + 1:]

# ask other servers
    # if found = send message to him
    if findInMapping(key) == True:
        server = mappingDict[key]
        s.sendto(data, ('127.0.0.1',server[3]))
    # if not found or got to the end of the url - send message to root
    else:
        s.sendto(data, ('127.0.0.1', int(mappingDict['root'])))
    recursive(data,s)

def recursive(data,s):
    #get answer
    newData, newSender_info = s.recvfrom(2048)
    print "Message: ", newData, " from: ", newSender_info, time.clock()
    #if = key - return
    if newData[0] == dataCopy[0]:
        return
    #else - GOT NEW DESTINATION
    #save in cache
    newData = newData.split(',')
    mappingDict[newData[0]] = newData
    # send him the data (newData = new dest)
    s.sendto(data, newData)
    recursive(data,s)

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
    findAnswerResolver(data,sender_info,s,source_ip,source_port)
    dataCopy = data.split(',')
    s.sendto(mappingDict[dataCopy[0]], sender_info)


