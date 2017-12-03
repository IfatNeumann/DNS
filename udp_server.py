from socket import socket, AF_INET, SOCK_DGRAM
import sys
import time
import ast
#local

# check if the ttl passed, and if so - delete from cache.
# return true if the key is ok, and false otherwise
def timeStampCheck(key):
    if findInMapping(key)==False:
        return False
    timeStamp = mappingDict[key][4]
    ttl = mappingDict[key][3]
    if timeStamp != '-1' and (time.clock() - float(timeStamp) > float(ttl) ):
        del mappingDict[key]
        return False
    return  True

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
    # search www.bob.com -> bob.com -> com
    key = data.split(',')[0][1:]
    # if found the url - return
    if findInMapping(key) == True and timeStampCheck(key):
        return True
    print "key: "+key+"findInMapping(key): "+str(findInMapping(key))+"timeStampCheck(key): "+str(timeStampCheck(key))
    # while the key is not in the cache or it is but the ttl passed:
    while (findInMapping(key) == False or (findInMapping(key) and timeStampCheck(key)==False)) and key.find('.') != -1:  # search NS
        key = key[key.find('.') + 1:]
        print "inside while: "+key
# ask other servers
    # if found = send message to him
    if findInMapping(key) and timeStampCheck(key):
        nsUrl = mappingDict[key][2]
        server = mappingDict[nsUrl]
        print str(server)
        s.sendto(data, ('127.0.0.1',int(server[2])))
    # if not found or got to the end of the url - send message to root
    else:
        s.sendto(data, ('127.0.0.1', int(mappingDict['root'])))
    return recursive(data,s)

def recursive(data,s):
    dataCopy = data[1:-1].split(',')
    #get answer
    newData, newSender_info = s.recvfrom(2048)
    print "Message: ", newData, " from: ", newSender_info, time.clock()
    first=""
    if newData == "not found":
        return False
    if newData.find('\n')!=-1:
        first = newData[:newData.find('\n')]
        first = ast.literal_eval(first)
        first.append(time.clock())
        #add to dict
        newKey = newData[1:-1].split(',')[0][1:-1]
        mappingDict[newKey] = first
        newData = newData[newData.find('\n')+1:]
    newKey = newData[1:-1].split(',')[0][1:-1]
    #if = key - return
    if newKey == dataCopy[0]:
        newData = ast.literal_eval(newData)
        newData[4] = time.clock()
        mappingDict[newKey] = newData
        return True
    #else - GOT NEW DESTINATION
    #save in cache
    newData = ast.literal_eval(newData)
    newData.append(time.clock())
    mappingDict[newData[0]] = newData
    # send him the data (newData = new dest)
    s.sendto(data, ('127.0.0.1', int(newData[2])))
    return recursive(data,s)

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
    l.append('-1')
    mappingDict[l[0]] = l
# add root to the dictionary
mappingDict['root'] = str(sys.argv[1])
s.bind((source_ip, source_port))
while True:
    data, sender_info = s.recvfrom(2048)
    print "Message: ", data, " from: ", sender_info, time.clock()
    if resolver:
        if findAnswerResolver(data,sender_info,s,source_ip,source_port):
            dataCopy = data[1:-1].split(',')
            s.sendto(str(mappingDict[dataCopy[0]]), sender_info)
        else:
            s.sendto("not found", sender_info)
    else:
        findAnswerNotResolver(data, sender_info, s)


