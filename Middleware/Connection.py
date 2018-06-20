import socket
import json

class RPCConnection:
    __sockfd = None
    __host = ''
    __port = 12388
    __rpcUser = ""
    __rpcPassword = ""
    __isOpen = False
    __isLogin = False

    def __init__(self,host,port,rpcUser,rpcPassword):
        self.__host = host
        self.__port = int(port)
        self.__rpcUser = rpcUser
        self.__rpcPassword = rpcPassword

        if self.__host == '':
            raise ValueError("Invalid Host (%s)" % self.__host)

        if self.__rpcUser == '':
            raise ValueError("Invalid rpcUser (%s)" % self.__rpcUser)

    def __login(self):
        payload = {"jsonrpc":"2.0","params":[self.__rpcUser,self.__rpcPassword],"id":"1","method":"login"}
        self.write(json.dumps(payload))
        recv_data = self.__recv_until_json_complete()
        result=json.loads(recv_data)
        if result.has_key('result'):
            self.__isLogin = True
        else:
            self.__isLogin = False

        return self.__isLogin


    def isAvailable(self):
        return (self.__isOpen and self.__isLogin)

    def open(self):
        if self.__host == '':
            return False
        else:
            self.__sockfd = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.__sockfd.connect((self.__host,self.__port))
            self.__isOpen = True
            self.__login()
    
    def close(self):
        if self.__isOpen :
            self.__sockfd.close()
            self.__sockfd = None
            self.__isOpen = False
            self.__isLogin = False

    def write(self,data):
        if self.__isOpen :
            return self.__sockfd.sendall(data)

    def __is_receive_complete(self,data):
        if data is None or data == '':
            return False
        json_start = False
        json_tag_count = 0
        for c in data:
            if c == '{':
                if not json_start:
                    json_start = True
                json_tag_count += 1
            elif c == '}':
                json_tag_count -= 1
            if json_start and json_tag_count == 0:
                return True
        return False

    def __recv_until_json_complete(self):
        left_data = ""
        while not self.__is_receive_complete(left_data):
            data = self.__sockfd.recv(4096)
            left_data += data
        return left_data

    def read(self):
        return self.__recv_until_json_complete()

    def isOpen(self):
        return self.__isOpen
