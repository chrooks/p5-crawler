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
parser = argparse.ArgumentParser(description='Uses the given login information to traverse FakeBook for 5 hidden secret keys')
parser.add_argument('username', type=str, help="FakeBook username")
parser.add_argument('password', type=str, help="FakeBook Password")
args = parser.parse_args()

### Setting up Host and Port ###
HOST = "fakebook.3700.network"
PORT = 443
CSRF = ""
COOKIE = ""

################################################################################

# Writes given log message to stderr
def log(string):
  if DEBUG: sys.stderr.write("DEBUG: " + string + "\n")

# Generates the GET Request with given headers
def get(domain, referer="", has_cookie=False):
    if (has_cookie):
        cookie_or_csrf = "csrftoken=" + CSRF + "; sessionid=" + COOKIE
    else:
        cookie_or_csrf = "csrftoken=" + CSRF

    ''' Implement gzip encoding '''
    request = "GET " + domain + " HTTP/1.1" + CRLF + \
              "Host: " + HOST + CRLF + \
              "Referer: " + referer + CRLF + \
              "Cookie: " + cookie_or_csrf + CRLF + CRLF
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


# Get the csrfmiddlewaretoken from given html
def get_csrfmiddlewaretoken(page):
    csrf_index = page.index("csrfmiddlewaretoken\" value=\"") + 28
    return page[csrf_index:].split("\"")[0]


# Get the csrftoken and sessionId from response
def get_csrftoken_and_cookie(request_response):
# cookie_index = response.index("Set-Cookie: sessionid=") + 22
# COOKIE = response[cookie_index + 1:].split(";")[0]


################################################################################


### Setting up the socket ###
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostbyname(HOST), PORT))  # Connects to the socket

context = ssl.create_default_context()
socket = context.wrap_socket(s, server_hostname=HOST)

### GET Request for login page (to get csrf token) ###
socket.send(get(domain='/accounts/login/?next=/fakebook/').encode())
page = socket.recv(3000).decode()

print(page)

# ### Parsing the login page to find the csrf ###
CSRF = get_csrfmiddlewaretoken(page)

# ### Creating the POST Request ###
body = f'next=/fakebook/&username={args.username}&password={args.password}&csrfmiddlewaretoken={CSRF}'
socket.send(post(domain='/accounts/login/', body=body).encode())
response = socket.recv(3000).decode()

if DEBUG: print(f"POST REQUEST RESPONSE\n{response}")

### Parsing the POST Response to find the cookie ###
# ''' Make helper to get the cookie'''
# cookie_index = response.index("Set-Cookie: sessionid=") + 22
# COOKIE = response[cookie_index + 1:].split(";")[0]
#
# ''' Use helper to get the csrf'''
#
#
# ### GET Request for homepage ###
# ''' Make helper to get the current location of the domain from the POST'''
# referer = 'https://fakebook.3700.network/accounts/login/?next=/fakebook/'
# socket.send(get(domain='/fakebook/', referer=referer, has_cookie=True).encode())
# page = socket.recv(3000).decode()
#
# print(page)
