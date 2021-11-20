#!/usr/bin/env python3

import sys
import argparse 
import socket
import ssl

### Debug ###
DEBUG = True
# DEBUG = False
CRLF = '\r\n'

### Argument Parser ####
parser = argparse.ArgumentParser(description='crawl the web')
parser.add_argument('username', type=str, help="Username")
parser.add_argument('password', type=str, help="Password")
args = parser.parse_args()

### Setting up Host and Port ###
HOST = "fakebook.3700.network"
PORT = 443
CSRF = ""
COOKIE = ""

# Writes given log message to stderr
def log(string):
  if DEBUG: sys.stderr.write("DEBUG: " + string + "\n")

# Generates the GET Request with given headers
def get(domain, referer=""):
    request = "GET " + domain + " HTTP/1.1" + CRLF + \
              "Host: " + HOST + CRLF + \
              "Referer: " + referer + CRLF + \
              "Accept-Encoding: gzip" + CRLF + \
              "Cookie: " + COOKIE + CRLF + CRLF
    if DEBUG: print(request)
    return request


# Generates the POST Request with given headers
def post(domain, body, has_cookie=False):
    # On initial login, there we do not have a cookie so we must pass the
    # csrf token in the cookie header
    if (has_cookie):
        cookie_or_csrf = COOKIE
    else:
        cookie_or_csrf = "csrftoken=" + CSRF

    request = "POST " + domain + " HTTP/1.1" + CRLF + \
              "Host: " + HOST + CRLF + \
              "Content-Type: application/x-www-form-urlencoded" + CRLF + \
              "Content-Length: " + str(len(body)) + CRLF + \
              "Accept-Encoding: gzip" + CRLF + \
              "Cookie: " + cookie_or_csrf + CRLF + CRLF + \
              body
    #if DEBUG: print(request)
    return request




################################################################################


### Setting up the socket ###
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostbyname(HOST), PORT))  # Connects to the socket

context = ssl.create_default_context()
socket = context.wrap_socket(s, server_hostname=HOST)

### GET Request for login page (to get csrf token) ###
socket.send(get(domain='/accounts/login/?next=/fakebook/').encode())
page = socket.recv(3000).decode()

### Parsing the login page to find the csrf ###
csrf_index = page.index(
    "csrfmiddlewaretoken\" value=\"") + 28  # length of string
CSRF = page[csrf_index:].split("\"")[0]

### Creating the POST Request ###
body = f'next=/fakebook/&username={args.username}&password={args.password}&csrfmiddlewaretoken={CSRF}'
socket.send(post(domain='/accounts/login/', body=body).encode())
response = socket.recv(3000).decode()

### Parsing the POST Response to find the cookie ###
cookie_index = response.index("Set-Cookie: sessionid=") + 22  # length of string
COOKIE = response[cookie_index + 1:].split(";")[0]

### GET Request for homepage ###
''' Make helper to get the current location of the domain from the POST'''
socket.send(get(domain='/fakebook/').encode())
page = socket.recv(3000).decode()

print(page)
