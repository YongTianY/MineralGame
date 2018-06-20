from Connection import RPCConnection
import Utils
import uuid
import json

class Wallet:
    __username = ''
    __password = ''
    __rpcConnection = None
    __isAuthentication = False

    def __init__(self, username, password,rpcConnection):
        self.__username = username
        self.__password = password
        self.__rpcConnection = rpcConnection
        
        if self.__rpcConnection == None:
            raise ValueError("Invalid Connection")

        if len(self.__username) <= 0:
            raise ValueError("Invalid Username (%s)" % self.__username)

        if len(self.__password) <= 8:
            raise ValueError("Invalid Password. at least 8 char")

    def open(self):
        self.close() #close first

        rid = str(uuid.uuid1())
        wallet_create={"jsonrpc":"2.0","params":[self.__username],"id":rid,"method":"wallet_open"}
        self.__rpcConnection.write(json.dumps(wallet_create))
        recv_data = self.__rpcConnection.read()
        result=json.loads(recv_data)
        print recv_data
        success = False
        if result['id'] == rid:
            if result.has_key('result') and result['result'] == None:
                success = True
            else:
                success = False
        else:
            success = False

        return success

    def close(self):
        rid = str(uuid.uuid1())
        payload={"jsonrpc":"2.0","params":[],"id":rid,"method":"wallet_close"}
        self.__rpcConnection.write(json.dumps(payload))
        recv_data = self.__rpcConnection.read()
        result=json.loads(recv_data)
        print recv_data
        success = False
        if result['id'] == rid:
            if result.has_key('result') and result['result'] == None:
                success = True
            else:
                success = False
        else:
            success = False

        return success

    def unlock(self):
        rid = str(uuid.uuid1())
        payload={"jsonrpc":"2.0","params":["9999",self.__password],"id":rid,"method":"wallet_unlock"}
        self.__rpcConnection.write(json.dumps(payload))
        recv_data = self.__rpcConnection.read()
        result=json.loads(recv_data)
        print "dsafsdaf " + recv_data
        
        success = False
        if result['id'] == rid:
            if result.has_key('result') and result['result'] == None:
                success = True
            else:
                success = False
        else:
            success = False

        return success
            
    def auth(self):
        auth = (self.open() and self.unlock())
        self.close()

        return auth

    @staticmethod 
    def newWallet(username,password,rpcConnection):
        if rpcConnection == None:
            raise ValueError("Invalid Connection")

        if len(username) <= 0:
            raise ValueError("Invalid Username (%s)" % username)

        if len(password) <= 8:
            raise ValueError("Invalid Password. at least 8 char")

        wallet = None
        rid = str(uuid.uuid1())
        wallet_create={"jsonrpc":"2.0","params":[username,password],"id":rid,"method":"wallet_create"}
        rpcConnection.write(json.dumps(wallet_create))

        recv_data = rpcConnection.read()
        result=json.loads(recv_data)
        print recv_data
        if result['id'] == rid:
            if result.has_key('result') and result['result'] == None:
                rid = str(uuid.uuid1())
                wallet_account_create={"jsonrpc":"2.0","params":[username],"id":rid,"method":"wallet_account_create"}
                rpcConnection.write(json.dumps(wallet_account_create))
                recv_data = rpcConnection.read()
                print recv_data
                result=json.loads(recv_data)
                address = ''
                if result.has_key('result'):
                    address = result['result']
                    
                rid = str(uuid.uuid1())
                wallet_close={"jsonrpc":"2.0","params":[],"id":rid,"method":"wallet_close"}
                rpcConnection.write(json.dumps(wallet_close))
                recv_data = rpcConnection.read()
                result=json.loads(recv_data)
                print recv_data
                if result['id'] == rid and result.has_key('result') and result['result'] == None:
                    wallet = Wallet(username,password,address,rpcConnection)
            elif result.has_key('error'):
                print result['error']
            else:
                print("Unknown Error \n %s" % recv_data)
        else:
            print recv_data

        return wallet             
    
