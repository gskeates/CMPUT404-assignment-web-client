#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2021 Graeme Keates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # Grab first line
        line_pattern = re.compile('HTTP/1.[01] [\S ]*[^\r\n]')
        line = line_pattern.match(data).group()

        # Grab code
        code_pattern = re.compile('\d{3,3}')
        code = code_pattern.search(line).group()

        return int(code)

    def get_headers(self, data):
        header, body = data.split('\r\n\r\n')
        return header

    def get_body(self, data):
        header, body = data.split('\r\n\r\n')
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        # Parse URL for information
        parsed_URL = urllib.parse.urlparse(url)

        if parsed_URL.port is None:
            port = 80
        else:
            port = parsed_URL.port
        host = parsed_URL.hostname

        # Create path
        path = parsed_URL.path
        if len(path) == 0:
            path = '/'

        # Format request
        request = "GET {} HTTP/1.1\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n".format(path, host)

        # Set up connection
        self.connect(host, port)

        # Send request
        self.sendall(request)

        # Receive response
        response = self.recvall(self.socket)

        # Close connection
        self.close()

        # Parse response for body and status code
        code = self.get_code(response)
        body = self.get_body(response)

        # Display server response
        # print(code)
        # print("Body = ", body)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        # Parse URL for information
        parsed_URL = urllib.parse.urlparse(url)
        if parsed_URL.port is None:
            port = 80
        else:
            port = parsed_URL.port
        host = parsed_URL.hostname

        # Create path
        path = parsed_URL.path
        if len(path) == 0:
            path = '/'

        # Format request
        if args is None:
            request = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nAccept: */*\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".format(path, host)
        else:
            query_string = urllib.parse.urlencode(args)
            request = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nAccept: */*\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}".format(path, host, len(query_string), query_string)

        # Set up connection
        self.connect(host, port)

        # Send request
        self.sendall(request)

        # Receive response
        response = self.recvall(self.socket)

        # Close connection
        self.close()

        # Parse response for body and status code
        code = self.get_code(response)
        body = self.get_body(response)

        # Display server response
        print(code)
        print(body)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
