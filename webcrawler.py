#!/usr/bin/env python3

'''
Your login credentials for Fakebook are:
username: brooks.ch
password: IO0VSGNDMCJ5E41Q
'''

import sys
import argparse
import socket
import ssl
import gzip
from bs4 import BeautifulSoup

# Headers 
STATS = "Status Code"
CONTY = "Content-Type"
CONLN = "Content-Length"
LOCAT = "Location"
SETCO = "Set-Cookie"

CNTNT = "Content"
CSRFT = "CSRF Token"
SESID = "Session ID"

RELEVANT_HEADERS = [STATS, CONTY, CONLN, LOCAT, SETCO]

# Globals 
HOST = "fakebook.3700.network"
PORT = 443
CSRF = ""
COOKIE = ""

DEBUG = True
# DEBUG = False

CRLF = '\r\n'

### Argument Parser ####
parser = argparse.ArgumentParser(
    description='Uses the given login information to traverse FakeBook for 5 hidden secret keys')
parser.add_argument('username', type=str, help="FakeBook username")
parser.add_argument('password', type=str, help="FakeBook Password")
args = parser.parse_args()

###############################################################################

# Writes given log message to stderr
def log(string):
    if DEBUG: sys.stderr.write("DEBUG: " + string + "\n")


# Generates the GET Request with given headers
def get(domain, csrf="", cookie=""):
    ''' Implement gzip encoding '''
    request = "GET " + domain + " HTTP/1.1" + CRLF + \
              "Host: " + HOST + CRLF + \
              "Cookie: " + "csrftoken=" + csrf + "; sessionid=" + cookie + CRLF + CRLF
    return request


# Generates the POST Request with given headers
def post(domain, body, csrf="", cookie=""):
    # On initial login, there we do not have a cookie so we must pass the
    # csrf token in the cookie header
    cookie_or_csrf = "csrftoken=" + csrf if (len(csrf) > 0) else cookie

    request = "POST " + domain + " HTTP/1.1" + CRLF + \
              "Host: " + HOST + CRLF + \
              "Content-Type: application/x-www-form-urlencoded" + CRLF + \
              "Content-Length: " + str(len(body)) + CRLF + \
              "Cookie: " + cookie_or_csrf + CRLF + CRLF + \
              body
    return request


# Creates and wraps a socket
def create_sock():
    log("Creating and wrapping socket...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostbyname(HOST), PORT))

    context = ssl.create_default_context()
    return context.wrap_socket(s, server_hostname=HOST)


# Get the csrfmiddlewaretoken from given html
def get_csrfmiddlewaretoken(page):
    csrf_index = page.index("csrfmiddlewaretoken\" value=\"") + 28
    return page[csrf_index:].split("\"")[0]


# parses a HTTP 1.1 response and converts it to a Dictionary
def parse_response(raw_response):
    # log("parse_response: Beginning. Building dictionary...")

    resp_list = raw_response.splitlines()
    dictionary = {}

    for ii in range(len(resp_list)):
        curr_line = resp_list[ii]

        if ii == 0:  # adds status on first line
            # log(f"parse_response: {ii}: added [{STATS}] = {curr_line[9:]}")
            dictionary[STATS] = curr_line[9:]

        elif curr_line == '':
            # adds content when first empty line is encountered
            # log(f"parse_response: {ii}: encountered empty line, adding rest of response to [{CNTNT}] field")
            rest = "".join(resp_list[ii + 1:-1])
            dictionary[CNTNT] = rest
            break

        else:
            (header, value) = curr_line.split(":", 1)
            value = value[1:]  # trim leading space

            if header in RELEVANT_HEADERS:

                if header == SETCO:
                    temp = value.split('=')
                    header = CSRFT if temp[0] == "csrftoken" else SESID
                    value = temp[1].split(';')[0]

                dictionary[header] = value
                # log(f"parse_response: {ii}: added [{header}] = {value}")

    log(f"parse_response: Finished building dictionary from response")
    return dictionary
  
# Goes through login protocol and returns the server's response containing the homepage
def login():
    ### Setting up the socket ###
    socket = create_sock()

    ### GET Request for login page (to get csrf token) ###
    log("Getting initial login page")
    socket.send(get(domain='/accounts/login/?next=/fakebook/').encode())
    response = parse_response(socket.recv(3000).decode())

    # ### Parsing the login page to find the csrf ###
    csrf_midware = get_csrfmiddlewaretoken(response[CNTNT])
    log(f"CSRF from the login page: {csrf_midware}")

    # ### POSTing login information ###
    log("Posting login information.")
    body = f'next=/fakebook/&username={args.username}&password={args.password}&csrfmiddlewaretoken={csrf_midware}'
    # ### Receiving response ###
    socket.send(post(domain='/accounts/login/', body=body, csrf=csrf_midware).encode())
    login_response = parse_response(socket.recv(
        3000).decode())  # Parsing the POST Response to find the cookie ###

    csrf = login_response[CSRFT]
    cookie = login_response[SESID]

    ### GET Request for homepage ###
    socket.send(get(domain=login_response[LOCAT], csrf=csrf, cookie=cookie).encode())
    login_response = parse_response(socket.recv(3000).decode())

    return login_response


################################################################################

response = login()
homepage = response[CNTNT]

log(homepage)

