#!/usr/bin/env python
# encoding: utf-8

import unittest
import random
import uuid

from Connection import RPCConnection
from WalletApi import Wallet
from ContractApi import Contract

class ContractApiTest(unittest.TestCase):
    __conn = None
    __wallet = None
    #CONGTXDtbsMjr1HzopNdttw3cK3SXQYNyWrq

    def setUp(self):
        self.__conn = RPCConnection('127.0.0.1',12388,'admin','admin')
        self.__conn.open()
        self.__wallet = Wallet("ace2","ye1320240",self.__conn)

    def tearDown(self):
        self.__wallet.close()
        self.__wallet = None
        self.__conn.close()
        self.__conn = None

    def test_Bets(self):
        contract = Contract(self.__conn,self.__wallet,"CONGTXDtbsMjr1HzopNdttw3cK3SXQYNyWrq")
        entryId,payId = contract.bets(1,0.1,str(uuid.uuid1()))
        print entryId
        print payId
        self.assertTrue(entryId != '')
        self.assertTrue(payId != '')

    def test_deBets(self):
        contract = Contract(self.__conn,self.__wallet,"CONGTXDtbsMjr1HzopNdttw3cK3SXQYNyWrq")
        entryId = contract.deBets(1,str(uuid.uuid1()))
        print "deBets " + entryId
        self.assertTrue(entryId != '')

    def test_queryResult(self):
        #2322535b42853772437c91b52bf6f441c5964292
        contract = Contract(self.__conn,self.__wallet,"CONGTXDtbsMjr1HzopNdttw3cK3SXQYNyWrq")
        data=contract.queryResult('92205f3dc7fb2a13692481bfa2ec357afd261784')
        self.assertTrue(data != '')
        print data



if __name__ == '__main__':
    unittest.main()
