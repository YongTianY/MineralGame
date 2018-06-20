#!/usr/bin/env python
# encoding: utf-8

import unittest

from Connection import RPCConnection

class ConnectionTest(unittest.TestCase):
    def test_create(self):
        with self.assertRaises(ValueError):
            conn = RPCConnection('',12388,"admin","admin")

        with self.assertRaises(ValueError):
            conn = RPCConnection('127.0.0.1',12388,'',"admin")    

        conn = RPCConnection('127.0.0.1',12388,'admin','admin')
        conn.open()
        self.assertTrue(conn != None)
        self.assertTrue(conn.isOpen())
        self.assertTrue(conn.isAvailable())

        conn.close()

        self.assertFalse(conn.isOpen())
        self.assertFalse(conn.isAvailable())

        conn = RPCConnection('127.0.0.1',12388,'adafsdf','asdfasf')
        conn.open()
        self.assertTrue(conn != None)
        self.assertTrue(conn.isOpen())
        self.assertFalse(conn.isAvailable())        
            
if __name__ == '__main__':
    unittest.main()
