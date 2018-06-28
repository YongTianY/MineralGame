#!/usr/bin/env python
# encoding: utf-8

import thread
import pty
import os
import paho.mqtt.client as mqtt
import Contants
import json
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64
import time
from WalletApi import Wallet
from Connection import RPCConnection
from ContractApi import Contract

def PtyWorker(pipe,t):
    master, slave = pty.openpty()
    slaveName = os.ttyname(slave)
    print slaveName
    os.system('rm -rf /home/leaf/localpipe')
    os.system('ln -s %s /home/leaf/localpipe' % slaveName)

    while pipe.isRunning():
        data = os.read(master, 256)
        print data
        pipe.on_contract_resp(data)

    print 'Exit'
    os.system('rm -rf /home/leaf/localpipe')
    pipe.disconnect()
        
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("Client.req")

def on_message(client, userdata, msg):
    if userdata != None:
        userdata.on_message(msg)


def MQTTWorker(pipe):
    client = mqtt.Client()
    client.reinitialise(client_id="", clean_session=True, userdata=pipe)
    client.on_connect = on_connect
    client.on_message = on_message
    pipe.setClient(client)
    client.connect("localhost", 1883, 60)
    client.loop_forever()   

class MiddlewareWorker:
    __Running = False
    __Client = None
    __KeyPool = {}
    __Conn = None
    __contractAddress = ''
    __chain_dir = ''

    def __init__(self,contractAddress,chain_dir):
        self.__contractAddress = contractAddress
        self.__chain_dir = chain_dir
        self.__Conn = RPCConnection('127.0.0.1',12388,'admin','admin')
        self.__Conn.open()

    def on_message(self,msg):
        if msg.topic == Contants.CLIENT_REQ_TOPIC:
            data = msg.payload.decode("utf-8")
            msgJSON = json.loads(data)
            params = msgJSON.params
            resp = {"clientID":params.clientID,"reqID":params.reqID,"result":""}
            if msgJSON.cmd == "Create":
                if self.__KeyPool.has_key(params.clientID):
                    key = self.__KeyPool[params.clientID]
                    rsakey = RSA.importKey(key)  # 导入读取到的私钥
                    cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
                    text = cipher.decrypt(base64.b64decode(params.data), None)

                    if text != None:
                        userinfo = json.loads(text)
                        if userinfo.has_key("name") and userinfo.has_key("password"):
                            r = os.path.exists(self.__chain_dir + "/wallets/" + userinfo.name)    
                            if r == True:
                                resp.result = {"code":Contants.CODE_FAILURE}
                            else:
                                wallet = Wallet.newWallet(userinfo.name,userinfo.password,self.__conn)
                                if wallet != None:
                                    resp.result = {"code":Contants.CODE_SUCCESS,"address":wallet.getAddress()}
                                else:
                                    resp.result = {"code":Contants.CODE_FAILURE}
                        else:
                            resp.result = {"code":Contants.CODE_FAILURE}
                    else:
                        resp.result = {"code":Contants.CODE_FAILURE}
                else:
                    resp.result = {"code":Contants.CODE_FAILURE}

                self.__Client.publish(params.clientID,json.dumps(resp),True)    
            elif msgJSON.cmd == "Auth_Key":
                if params.has_key('key'):
                    self.__KeyPool[params.clientID] = params.key
                    resp.result = {"code":Contants.CODE_SUCCESS}
                else:
                    resp.result = {"code":Contants.CODE_FAILURE}

                self.__Client.publish(params.clientID,json.dumps(resp),True)     
            elif msgJSON.cmd == "Login":
                if self.__KeyPool.has_key(params.clientID):
                    key = self.__KeyPool[params.clientID]
                    rsakey = RSA.importKey(key)  # 导入读取到的私钥
                    cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
                    text = cipher.decrypt(base64.b64decode(params.data), None)

                    if text != None:
                        userinfo = json.loads(text)
                        wallet = Wallet(userinfo.name,userinfo.password,self.__Conn)
                        ret = wallet.auth()
                        if ret == True:
                            resp.result = json.dumps({"code":Contants.CODE_SUCCESS})
                        else:
                            resp.result = json.dumps({"code":Contants.CODE_FAILURE})
                    else:
                        resp.result = json.dumps({"code":Contants.CODE_DECRYPT_ERROR})
                else:
                    resp.result = json.dumps({"code":Contants.CODE_MISS_PUBLIC_KEY})

                self.__Client.publish(params.clientID,json.dumps(resp),True)                        
            elif msgJSON.cmd == "Bets":
                if self.__KeyPool.has_key(params.clientID):
                    key = self.__KeyPool[params.clientID]
                    rsakey = RSA.importKey(key)  # 导入读取到的私钥
                    cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
                    text = cipher.decrypt(base64.b64decode(params.data), None)

                    if text != None:
                        userinfo = json.loads(text)
                        wallet = Wallet(userinfo.name,userinfo.password,self.__Conn)
                        ret = wallet.auth()
                        if ret == True:
                            contract = Contract(self.__conn,wallet,self.__contractAddress)
                            entryId,payId = contract.bets(paprams.target,params.amount,params.reqId)
                            if entryId != '' and payId != '':
                                resp.result = json.dumps({"code":Contants.CODE_SUCCESS,"entryId":entryId,"payId":payId})
                            else:
                                resp.result = json.dumps({"code":Contants.CODE_FAILURE})
                        else:
                            resp.result = json.dumps({"code":Contants.CODE_FAILURE})
                    else:
                        resp.result = json.dumps({"code":Contants.CODE_DECRYPT_ERROR})
                else:
                    resp.result = json.dumps({"code":Contants.CODE_MISS_PUBLIC_KEY})

                self.__Client.publish(params.clientID,json.dumps(resp),True)
            elif msgJSON.cmd == "deBets":
                if self.__KeyPool.has_key(params.clientID):
                    key = self.__KeyPool[params.clientID]
                    rsakey = RSA.importKey(key)  # 导入读取到的私钥
                    cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
                    text = cipher.decrypt(base64.b64decode(params.data), None)

                    if text != None:
                        userinfo = json.loads(text)
                        wallet = Wallet(userinfo.name,userinfo.password,self.__Conn)
                        ret = wallet.auth()
                        if ret == True:
                            contract = Contract(self.__conn,wallet,self.__contractAddress)
                            entryId = contract.deBets(paprams.target,params.reqId)
                            if entryId != '':
                                resp.result = json.dumps({"code":Contants.CODE_SUCCESS,"entryId":entryId})
                            else:
                                resp.result = json.dumps({"code":Contants.CODE_FAILURE})   
                        else:
                            resp.result = json.dumps({"code":Contants.CODE_FAILURE})
                    else:
                        resp.result = json.dumps({"code":Contants.CODE_DECRYPT_ERROR})
                else:
                    resp.result = json.dumps({"code":Contants.CODE_MISS_PUBLIC_KEY})

                self.__Client.publish(params.clientID,json.dumps(resp),True)
            elif msgJSON.cmd == "Transfer_to":
                if self.__KeyPool.has_key(params.clientID):
                    key = self.__KeyPool[params.clientID]
                    rsakey = RSA.importKey(key)  # 导入读取到的私钥
                    cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
                    text = cipher.decrypt(base64.b64decode(params.data), None)

                    if text != None:
                        userinfo = json.loads(text)
                        wallet = Wallet(userinfo.name,userinfo.password,self.__Conn)
                        ret = wallet.auth()
                        if ret == True:
                            entryId = wallet.pay(userinfo.address,False,userinfo.amount,'ACT')
                            if entryId == '':
                                resp.result = json.dumps({"code":Contants.CODE_TRANSFER_FAILURE})
                            else:
                                resp.result = json.dumps({"entryId" : entryId,"code":Contants.CODE_SUCCESS})
                        else:
                            resp.result = json.dumps({"code":Contants.CODE_FAILURE})
                    else:
                        resp.result = json.dumps({"code":Contants.CODE_DECRYPT_ERROR})
                else:
                    resp.result = json.dumps({"code":Contants.CODE_MISS_PUBLIC_KEY})

                self.__Client.publish(params.clientID,json.dumps(resp),True)
            elif msgJSON.cmd == "backup_pk":
                if self.__KeyPool.has_key(params.clientID):
                    key = self.__KeyPool[params.clientID]
                    rsakey = RSA.importKey(key)  # 导入读取到的私钥
                    cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
                    text = cipher.decrypt(base64.b64decode(params.data), None)

                    if text != None:
                        userinfo = json.loads(text)
                        wallet = Wallet(userinfo.name,userinfo.password,self.__Conn)
                        ret = wallet.auth()
                        if ret == True:
                            key = wallet.getPrivateKey()                             
                            resp.result = json.dumps({"pk":key,"code":Contants.CODE_SUCCESS})
                        else:
                            resp.result = json.dumps({"code":Contants.CODE_FAILURE})
                    else:
                        resp.result = json.dumps({"code":Contants.CODE_DECRYPT_ERROR})
                else:
                    resp.result = json.dumps({"code":Contants.CODE_MISS_PUBLIC_KEY})

                self.__Client.publish(Contants.SERVER_RESP_TOPIC,json.dumps(resp),True)
            elif msgJSON.cmd == "Query_balance":
                if self.__KeyPool.has_key(params.clientID):
                    key = self.__KeyPool[params.clientID]
                    rsakey = RSA.importKey(key)  # 导入读取到的私钥
                    cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
                    text = cipher.decrypt(base64.b64decode(params.data), None)

                    if text != None:
                        userinfo = json.loads(text)
                        wallet = Wallet(userinfo.name,userinfo.password,self.__Conn)
                        ret = wallet.auth()
                        if ret == True:
                            amount = wallet.amount()
                            
                            resp.result = json.dumps({"amount":amount,"code":Contants.CODE_SUCCESS})
                        else:
                            resp.result = json.dumps({"code":Contants.CODE_FAILURE})
                    else:
                        resp.result = json.dumps({"code":Contants.CODE_DECRYPT_ERROR})
                else:
                    resp.result = json.dumps({"code":Contants.CODE_MISS_PUBLIC_KEY})

                self.__Client.publish(Contants.SERVER_RESP_TOPIC,json.dumps(resp),True)
            else:
                resp.result = json.dumps({"code":Contants.CODE_FAILURE})
                self.__Client.publish(Contants.SERVER_RESP_TOPIC,json.dumps(resp),True)

    def isRunning(self):
        return self.__Running
    
    def on_contract_resp(self,data):
        pass

    def setClient(self,client):
        self.__Client = client
    
    def disconnect(self):
        if self.__Client != None:
            self.__Client.disconnect()
            self.__Client = None

        if self.__Conn != None:
            self.__Conn.close()
            self.__Conn = None

    def start(self):
        self.__Running = True
        thread.start_new_thread(PtyWorker,(self,1))
        MQTTWorker(self)
        
    def stop(self):
        __Running = False


if __name__ == '__main__':
    myWorker=MiddlewareWorker("Contract Address","chain_dir")
    myWorker.start()

    while True :
        time.sleep(10)
    
