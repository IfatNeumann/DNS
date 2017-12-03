from socket import socket, AF_INET, SOCK_DGRAM
import sys
import time
import ast
#local
#arguments: [my IP] [my port] [mapping file name] [my root server] [resolver or not]

# check if the ttl passed, and if so - delete from cache.
# return true if the key is ok, and false otherwise
def findInCache(key):
    if not(key in cache):
        return False
    timeStamp = cache[key][4]
    ttl = cache[key][3]
    if timeStamp != '-1' and (time.clock() - float(timeStamp) > float(ttl) ):
        del cache[key]
        return False
    return  True

def findAnswerNotResolver(data,sender_info,s):
    dataCopy = data[1:-1].split(',')

    # search www.bob.com -> bob.com -> com
    key = data.split(',')[0][1:]
    while findInCache(key) == False and key.find('.') != -1:  # search NS
        key = key[key.find('.') + 1:]

    # if found - send details
    if key in cache:
        if key == dataCopy[0]:
            msg = str(cache[key])
        else:
            # found a helpful NS
            nsUrl = cache[key][2]
            # send the NS and it's Ip
            msg = str(cache[key]) + "\n" + str(cache[nsUrl])

    # if not found or got to the end of the url
    else:
        msg = "not found"
    s.sendto(msg, sender_info)

def findAnswerResolver(data,sender_info,s,source_ip,source_port):
    # search www.bob.com -> bob.com -> com
    key = data.split(',')[0][1:]
    # if found the url - return
    if key in cache:
        return True

    # while the key is not in the cache or it is but the ttl passed:
    while findInCache(key) == False and key.find('.') != -1:
        # search NS
        key = key[key.find('.') + 1:]
# ask other servers

    # if found = send message to him
    if findInCache(key):
        nsUrl = cache[key][2]
        server = cache[nsUrl]
        s.sendto(data, ('127.0.0.1',int(server[2])))
    # if not found or got to the end of the url - send message to root
    else:
        s.sendto(data, ('127.0.0.1', int(cache['root'])))
    return recursive(data,s)

def recursive(data,s):
    dataCopy = data[1:-1].split(',')
    #get answer
    newData, newSender_info = s.recvfrom(2048)
    print "Message: ", newData, " from: ", newSender_info, time.clock()
    if newData == "not found":
        return False
    # if we got a GluedRR massage
    if newData.find('\n')!=-1:
        first = newData[:newData.find('\n')]
        first = ast.literal_eval(first)
        first.append(time.clock())

        #add to cache the first one
        newKey = newData[1:-1].split(',')[0][1:-1]
        cache[newKey] = first
        newData = newData[newData.find('\n')+1:]

    newKey = newData[1:-1].split(',')[0][1:-1]
    #if = key - return
    if newKey == dataCopy[0]:
        newData = ast.literal_eval(newData)
        newData[4] = time.clock()
        cache[newKey] = newData
        return True
    #else - GOT NEW DESTINATION to ask

    #save in cache
    newData = ast.literal_eval(newData)
    newData.append(time.clock())
    cache[newData[0]] = newData
    # send him the data (newData = new dest)
    s.sendto(data, ('127.0.0.1', int(newData[2])))
    return recursive(data,s)

# initialize resolver
resolver = False
if str(sys.argv[5]) == "resolver":
    resolver = True

s = socket(AF_INET, SOCK_DGRAM)
source_ip = sys.argv[1]
source_port = sys.argv[2]

# save mapping's data in a dictionary
mappingFile=open(sys.argv[3],"r")
cache = {}
for line in mappingFile:
    l = line.split()
    l.append('-1')
    cache[l[0]] = l

# add root to the cache
cache['root'] = str(sys.argv[4])
s.bind((source_ip, int(source_port)))

while True:
    data, sender_info = s.recvfrom(2048)
    print "Message: ", data, " from: ", sender_info, time.clock()
    if resolver:
        if findAnswerResolver(data,sender_info,s,source_ip,source_port):
            dataCopy = data[1:-1].split(',')
            s.sendto(str(cache[dataCopy[0]]), sender_info)
        else:
            s.sendto("not found", sender_info)
    else:
        findAnswerNotResolver(data, sender_info, s)