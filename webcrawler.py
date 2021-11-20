#!/usr/bin/env python3

import argparse, socket, ssl

### Debug ###
# DEBUG = True
DEBUG = False
CRLF = '\r\n'

### Argument Parser ####
parser = argparse.ArgumentParser(description='crawl the web')
parser.add_argument('username', type=str, help="Username")
parser.add_argument('password', type=str, help="Password")
args = parser.parse_args()

### Setting up Host and Port ###
host = "fakebook.3700.network"
port = 443
cookie = ""


# Generates the GET Request with given headers
def get(domain, referer=""):
    request = "GET " + domain + " HTTP/1.1" + CRLF + \
              "Host: " + host + CRLF + \
              "Referer: " + referer + CRLF + \
              "Cookie: " + cookie + CRLF + CRLF
    if DEBUG: print(request)
    return request


# Generates the POST Request with given headers
def post(domain, body):
    request = "POST " + domain + " HTTP/1.1" + CRLF + \
              "Host: " + host + CRLF + \
              "Content-Type: application/x-www-form-urlencoded" + CRLF + \
              "Content-Length: " + str(len(body)) + CRLF + \
              "Cookie: csrftoken=" + cookie + CRLF + CRLF + \
              body
    if DEBUG: print(request)
    return request


################################################################################


### Setting up the socket ###
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostbyname(host), port))  # Connects to the socket

context = ssl.create_default_context()
socket = context.wrap_socket(s, server_hostname=host)

### GET Request for login page (to get csrf token) ###
socket.send(get(domain='/accounts/login/?next=/fakebook/').encode())
login_page = socket.recv(3000).decode()

### Getting the csrf (cookie) from the login page ###
csrf_index = login_page.index(
    "csrfmiddlewaretoken\" value=\"") + 28  # length of string
cookie = login_page[csrf_index:].split("\"")[0]

### Creating the POST Request ###
body = f'next=/fakebook/&username={args.username}&password={args.password}&csrfmiddlewaretoken={cookie}'
socket.send(post(domain='/accounts/login/', body=body).encode())

print(socket.recv(3000).decode())
