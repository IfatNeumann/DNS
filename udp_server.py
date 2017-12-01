from socket import socket, AF_INET, SOCK_DGRAM
import sys
import time
#local
def findInMapping(url):
    if url in mappingDict:
        return True
    else:
        return False

def findAnswer(data,sender_info,s):
    dataCopy = data.split(',')
    print dataCopy[0]
    # search www.bob.com -> bob.com -> com
    key = data.split(',')[0][1:]
    while findInMapping(key) == False and key.find('.') != -1:  # search NS
        key = key[key.find('.') + 1:]
    # search in other servers
    # if found = send message
    if findInMapping(key) == True:
        msg = mappingDict[key][2]
        s.sendto(msg, sender_info)  # iterate or recursive
    # if not found or got to the end of the url - try root
    else:
        s.sendto(data, ('127.0.0.1', int(mappingDict['root'])))
    newData, newSender_info = s.recvfrom(2048)
    print "Message: ", newData, " from: ", newSender_info, time.clock()
    # save in cache
    newData = newData.split(',')
    mappingDict[newData[0]] = newData
    # if it's tha answer - return to the client
    if newData[0] == dataCopy[0]:
        return
    else:
        findAnswer(data, sender_info, s)


                #   s.sendto(msg, (source_ip, source_port))

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
    findAnswer(data,sender_info,s)
    dataCopy = data.split(',')
    s.sendto(mappingDict[dataCopy[0]], sender_info)


