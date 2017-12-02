from socket import socket, AF_INET, SOCK_DGRAM
import sys
import time
import ast
#local
def findInMapping(url):
    if url in mappingDict:
        return True
    else:
        return False

def findAnswerNotResolver(data,sender_info,s):
    dataCopy = data[1:-1].split(',')
    # search www.bob.com -> bob.com -> com
    key = data.split(',')[0][1:]
    while findInMapping(key) == False and key.find('.') != -1:  # search NS
        key = key[key.find('.') + 1:]
    # if found = send details
    if findInMapping(key) == True:
        if key == dataCopy[0]:
            msg = str(mappingDict[key])
        else:
            # found a helpful NS
            nsUrl = mappingDict[key][2]
            # send the NS and it's Ip
            msg = str(mappingDict[key]) + "\n" + str(mappingDict[nsUrl])
    # if not found or got to the end of the url
    else:
        msg = "not found"
    s.sendto(msg, sender_info)

def findAnswerResolver(data,sender_info,s,source_ip,source_port):
    dataCopy = data[-1:1].split(',')
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
        nsUrl = mappingDict[key][2]
        server = mappingDict[nsUrl]
        s.sendto(data, ('127.0.0.1',server[3]))
    # if not found or got to the end of the url - send message to root
    else:
        s.sendto(data, ('127.0.0.1', int(mappingDict['root'])))
    recursive(data,s)

def recursive(data,s):
    dataCopy = data[1:-1].split(',')
    #get answer
    newData, newSender_info = s.recvfrom(2048)
    print "Message: ", newData, " from: ", newSender_info, time.clock()
    first=""
    if newData.find('\n')!=-1:
        first = newData[:newData.find('\n')]
        #add to dict
        newKey = newData[1:-1].split(',')[0][1:-1]
        mappingDict[newKey] = ast.literal_eval(first)
        newData = newData[newData.find('\n')+1:]
    newKey = newData[1:-1].split(',')[0][1:-1]
    #if = key - return
    if newKey == dataCopy[0]:
        mappingDict[newKey] = ast.literal_eval(newData)
        return
    #else - GOT NEW DESTINATION
    #save in cache
    newData = ast.literal_eval(newData)
    mappingDict[newData[0]] = newData
    # send him the data (newData = new dest)
    s.sendto(data, ('127.0.0.1', int(newData[2])))
    recursive(data,s)

# initialize resolver
resolver = False
if str(sys.argv[2]) == "resolver":
    resolver = True

s = socket(AF_INET, SOCK_DGRAM)
source_ip = '0.0.0.0'
source_port = 12445

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
    if resolver:
        findAnswerResolver(data,sender_info,s,source_ip,source_port)
        dataCopy = data[1:-1].split(',')
        s.sendto(str(mappingDict[dataCopy[0]]), sender_info)
    else:
        findAnswerNotResolver(data, sender_info, s)


