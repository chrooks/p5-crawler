#!/usr/bin/env python3

import argparse, socket, ssl

### Debug ###
# DEBUG = True
DEBUG = False

### Argument Parser ####
parser = argparse.ArgumentParser(description='crawl the web')
parser.add_argument('username', type=str, help="Username")
parser.add_argument('password', type=str, help="Password")
args = parser.parse_args()

######################################################################################

### Setting up Host and Port ###
host = "fakebook.3700.network"
port = 443

### Creating the POST Request ###
### FROM: https://stackoverflow.com/questions/28670835/python-socket-client -post-parameters ####
headers = """\
POST accounts/login/ HTTP/1.1\r
Content-Type: {content_type}\r
Content-Length: {content_length}\r
Host: {host}\r
Connection: close\r
\r\n"""

body = f'next=/fakebook/&username={args.username}&password={args.password}'
body_bytes = body.encode('ascii')
header_bytes = headers.format(
    content_type="application/x-www-form-urlencoded",
    content_length=len(body_bytes),
    host=str(host) + ":" + str(port)
).encode('iso-8859-1')

payload = header_bytes + body_bytes

### Setting up the socket ###
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostbyname(host), port))  # Connects to the socket

context = ssl.create_default_context()
socket = context.wrap_socket(s, server_hostname=host)

print(payload)

socket.sendall(payload)

print(socket.recv().decode())