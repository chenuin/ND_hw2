#!/usr/bin/env python  
# -*- coding:utf8 -*-  
  
import sys  
#reload(sys)  
#sys.setdefaultencoding('utf-8')  
import threading
import socket
import getpass
import time

class color:
    end =  "\033[0m"
    black = "\033[30m"
    red =   "\033[31m"
    green = "\033[32m"
    yellow ="\033[33m"
    blue =  "\033[34m"
    purple ="\033[35m"
    cyan =  "\033[36m"
    grey =  "\033[37m"

def strDecode(string):
    bytes_str = string.decode('utf-8', "replace")
    return (bytes_str)

def strEncode(string):
    bytes_str = string.encode('UTF-8')
    return (bytes_str)

def printStatus(string):
    if string == "none":
        print ("none")
    else:
        strON, strOFF = string.split(";")

        onList = strON.split(",")
        offList = strOFF.split(",")
        for i in range(0, len(onList), 1):
            if onList[i] == "":
                break;
            print(" {0:10} : online".format(onList[i]))
        for i in range(0, len(offList), 1):
            if offList[i] == "":
                break;
            print(" {0:10} : offline".format(offList[i]))

def sendFile(sock, fileName):
    try:
        sfile = open(fileName, 'rb')
    except Exception as msg:
        sys.stderr.write("%s\n" % msg)
    else:
        while True:   
            data = sfile.read(1024)
            if not data:   
                break
            while len(data) > 0:   
                intSent = sock.send(data)
                data = data[intSent:]  
  
    time.sleep(3)
    data = strEncode('EOF')
    sock.sendall(data)
    
    print ('[END] Transmission finish')

def recvFile(sock, fileName):
    tmpName = fileName.split('.')
    saveName = str(time.time()) + "." + tmpName[1]
    f = open(saveName, 'wb')   
    while True:   
        data = sock.recv(1024)
        #print (data)
        if data == b'EOF':
            break
        
        f.write(data)   
                           
    f.flush()   
    f.close()   
  
    print ('[END] Download finish')

def Send(sock, test):
    while True:
        data = input('> ')
        data = strEncode(data)
        sock.send(data)
        if strDecode(data) == 'exit':
            break

def Recv(sock, test):
    while True:
        data = sock.recv(1024)
        data = strDecode(data)
        if data[:2] == "::":
            printStatus(data[2:])
        else:
            print (data)
        if data[:3] == "[5]":       # data = [5] start transmit
            buf1, fileName, buf2 = data.split('"')
            #print (fileName)
            data = strEncode("start")
            sock.send(data)
            sendFile(sock, fileName)
        elif data[:3] == "[6]":     # data = [6] start receive
            buf1, fileName, buf2 = data.split('"')
            recvFile(sock, fileName)
        if data == color.blue+'Good bye'+color.end:
            sock.close()
            break

class ClientThread(object):  
    def __init__(self, clientSock):
        self.socket = clientSock

    def tcpclient(self):
        threads = []
        # send to server
        msg = strEncode("Data send from client")
        sendDataLen = self.socket.send(msg)
        #print ("sendDataLen: {}".format(sendDataLen))
        
        # Server reply(welcome)
        recvData = self.socket.recv(1024)
        #print ("%s"%strDecode(recvData))
        
        # login
        if self.login():
            print(color.green+'Login Success'+color.end)
            
            chat = threading.Thread(target = Send, args = (self.socket,None))
            threads.append(chat) 
            chat = threading.Thread(target = Recv, args = (self.socket,None))
            threads.append(chat)
            for i in range(len(threads)):
                threads[i].start()
            threads[0].join()
        else:
            print(color.red+'Login Fail'+color.end)

        #clientSock.close()

    def login(self):
        user = input('login: ')
        sendDataLen = self.socket.send(strEncode(user))
        pwd = getpass.getpass('password: ')
        sendDataLen = self.socket.send(strEncode(pwd))
        
        # Server reply login result
        recvData = self.socket.recv(1024)
        recvData = strDecode(recvData)
        print (recvData)
        if recvData == "Success":
            return 1
        else:
            return 0
          
if __name__ == "__main__":
    host = "0.0.0.0"
    port = 9999
    try:
        clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSock.connect((host,port))
        
        netClient = ClientThread(clientSock)
        netClient.tcpclient()
    except Exception as msg:
        sys.stderr.write("%s\n" % msg)
