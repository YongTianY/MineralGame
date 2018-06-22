import Utils
import uuid
import json

from Connection import RPCConnection
from WalletApi import Wallet

class Contract:
    __conn = None
    __wallet = None
    __address = None

    def __init__(self,conn,wallet,contractAddress):
        self.__conn = conn
        self.__wallet = wallet
        self.__address = contractAddress
    
    def deBets(self,target,reqId):
        walletAddress = self.__wallet.getAddress()    
        self.__wallet.open()
        self.__wallet.unlock()
        rid = str(uuid.uuid1())
        
        param = "%s|%s|%s" % (walletAddress,target,reqId)
        payload={"jsonrpc":"2.0","params":[self.__address,self.__wallet.getUsername(),"deBets",param,"ACT","1"],"id":rid,"method":"call_contract"}
        self.__conn.write(json.dumps(payload))
        recv_data = self.__conn.read()
        result=json.loads(recv_data)
        if result['id'] == rid and result.has_key('result'):
            resp = result['result']
            if resp.has_key('entry_id'):
                entryId = resp['entry_id']

        self.__wallet.close()
                
        return entryId

    def bets(self,target,amount,reqId):
        rid = str(uuid.uuid1())
        payId = ''
        entryId = ''
        if float(self.__wallet.amount()) < float(amount):
            return entryId,payId
        else:
            walletAddress = self.__wallet.getAddress()
            self.__wallet.open()
            self.__wallet.unlock()
            
            param = "%s|%s|%s|%s" % (walletAddress,target,amount,reqId)
            print param
            payload={"jsonrpc":"2.0","params":[self.__address,self.__wallet.getUsername(),"bets",param,"ACT","1"],"id":rid,"method":"call_contract"}
            self.__conn.write(json.dumps(payload))
            recv_data = self.__conn.read()
            print recv_data
            result=json.loads(recv_data)
            if result['id'] == rid and result.has_key('result'):
                resp = result['result']
                if resp.has_key('entry_id'):
                    entryId = resp['entry_id']
                    
                    #wallet.pay("CONKtJjMJ4CkrL1gMQhLbuWsyScYchgdrnYL",True,"0.1",'ACT')
                    payId = self.__wallet.pay(self.__address,True,amount,"ACT")
                    if payId == '':
                        self.deBets()
                        entryId = ''
        
            self.__wallet.close()
               
        return entryId,payId
    
    def queryResult(self,entryId):
        ret = ''
        rid = str(uuid.uuid1())
        payload={"jsonrpc":"2.0","params":[entryId],"id":rid,"method":"blockchain_get_contract_result"}
        self.__conn.write(json.dumps(payload))
        recv_data = self.__conn.read()
        print recv_data
        result=json.loads(recv_data)
        if result['id'] == rid and result.has_key('result'):
            resp = result['result']
            bn = resp['block_num']
            trxId = resp['trx_id']

            rid = str(uuid.uuid1())
            payload={"jsonrpc":"2.0","params":[bn,trxId],"id":rid,"method":"blockchain_get_events"}
            self.__conn.write(json.dumps(payload))
            recv_data = self.__conn.read()
            print recv_data
            result=json.loads(recv_data)

            if result['id'] == rid and result.has_key('result'):
                res = result['result']
                ret = res[0]['event_param']

        return ret

