from unittest import TestCase
from unittest import mock
import unittest
import clock
import time
from multiprocessing import Process
import os
import socket
from _thread import *
import threading
import time
from threading import Thread
from collections import deque

FORMAT = 'ascii'
BYTE_ORDER = 'big'

class TestClock(TestCase):

    def test_machine(self, ):
        localHost= "127.0.0.1"
        port1 = 18001
        port2 = 28001
        port3 = 38001

        config1=[localHost, port1, port2]
        config1.append(os.getpid())

        config2=[localHost, port2, port1]
        config2=[localHost, ]




if __name__ == '__main__':
    unittest.main()