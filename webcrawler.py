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
host = "https://fakebook.3700.network/accounts/login/?next=/fakebook/"
port = 443

### Creating the POST Request ###
headers = """\
POST /auth HTTP/1.1\r
Content-Type: {content_type}\r
Content-Length: {content_length}\r
Host: {host}\r
Connection: close\r
\r\n"""

body = f'userName={args.username}&password={args.password}'
body_bytes = body.encode('ascii')
header_bytes = headers.format(
    content_type="application/x-www-form-urlencoded",
    content_length=len(body_bytes),
    host=str(host) + ":" + str(port)
).encode('iso-8859-1')

payload = header_bytes + body_bytes

### Setting up the socket ###
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect((socket.gethostbyname(host), port))  # Connects to the socket

context = ssl.create_default_context()
socket = context.wrap_socket(s, server_hostname=host)

print(socket.sendall(payload))