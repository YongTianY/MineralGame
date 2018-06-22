#!/usr/bin/env python
# encoding: utf-8

import unittest
import random

from Connection import RPCConnection
from WalletApi import Wallet

class WalletTest(unittest.TestCase):
    __conn = None

    def setUp(self):
        self.__conn = RPCConnection('127.0.0.1',12388,'admin','admin')
        self.__conn.open()

    def tearDown(self):
        self.__conn.close()
        self.__conn = None

    def test_create(self):
        with self.assertRaises(ValueError):
            wallet = Wallet.newWallet("ace2","1234",self.__conn)

        with self.assertRaises(ValueError):
            wallet = Wallet.newWallet("","123456789",self.__conn)

        with self.assertRaises(ValueError):
            wallet = Wallet.newWallet("ace2","123456789",None)
     
        wallet = Wallet.newWallet("ace" + str(random.randint(3,3000)),"ye1320240",self.__conn)
        self.assertTrue(wallet.getAddress() != '')  
        print wallet.getAddress()
        #ACTGFnDVEgn8GcC3ZdexfnEa6EBrU67wAocH

    def test_getAddress(self):
        wallet = Wallet("ace2","ye1320240",self.__conn)
        self.assertTrue(wallet.getAddress() == 'ACTGFnDVEgn8GcC3ZdexfnEa6EBrU67wAocH')
        wallet.close()

    def test_getPrivateKey(self):
        #5JnAudSiYXeatFAUR9HRhR9ZQCfF7bPT4KBJPdWMsdLVnUCVHzS
        wallet = Wallet("ace2","ye1320240",self.__conn)
        self.assertTrue(wallet.getPrivateKey() == '5JnAudSiYXeatFAUR9HRhR9ZQCfF7bPT4KBJPdWMsdLVnUCVHzS')
        wallet.close()
    
    def test_amount(self):
        wallet = Wallet("ace2","ye1320240",self.__conn)
        self.assertTrue(wallet.amount() > 1)
        wallet.close()

    def test_pay(self):
        #receiver ACT6b6VTNjRaJVTxYMfAZfB1TZkZ7jyc3eJU
        #contract CONKtJjMJ4CkrL1gMQhLbuWsyScYchgdrnYL
        wallet = Wallet("ace2","ye1320240",self.__conn)
        entryId = wallet.pay("ACT6b6VTNjRaJVTxYMfAZfB1TZkZ7jyc3eJU",False,"101",'ACT')
        self.assertFalse(entryId != '')

        entryId = wallet.pay("ACT6b6VTNjRaJVTxYMfAZfB1TZkZ7jyc3eJU",False,"0.1",'ACT')
        self.assertTrue(entryId != '')
        print "Entry Id : " + entryId
            
        entryId = wallet.pay("CONKtJjMJ4CkrL1gMQhLbuWsyScYchgdrnYL",True,"0.1",'ACT')
        self.assertTrue(entryId != '')
        print "Contract Entry Id : " + entryId

    def test_op(self):
        with self.assertRaises(ValueError):
            wallet = Wallet("ace2","1234",self.__conn)
        with self.assertRaises(ValueError):
            wallet = Wallet("","123456789",self.__conn)
        with self.assertRaises(ValueError):
            wallet = Wallet("ace2","123456789",None)

        wallet = Wallet("ace2","ye1320240",self.__conn)
        wallet.close()
        self.assertTrue(wallet.open())
        self.assertTrue(wallet.unlock())
        
        wallet.close()
        self.assertTrue(wallet.auth())
    
if __name__ == '__main__':
    unittest.main()
