#!/usr/bin/env python
# encoding: utf-8

import unittest

from Connection import RPCConnection
from Wallet import Wallet

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
     
        #self.assertTrue(wallet == None)
        #wallet = Wallet.newWallet("ace2","ye1320240",self.__conn)  
        #ACTGFnDVEgn8GcC3ZdexfnEa6EBrU67wAocH

    def test_open(self):
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
