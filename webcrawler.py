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

### Debug ###
DEBUG = True
# DEBUG = False

CRLF = '\r\n'

STATS = "Status Code"
CONTY = "Content-Type"
CONLN = "Content-Length"
LOCAT = "Location"
SETCO = "Set-Cookie"

CNTNT = "Content"
CSRFT = "CSRF Token"
SESID = "Session ID"

RELEVANT_HEADERS = [STATS, CONTY, CONLN, LOCAT, SETCO]

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

###############################################################################

# Writes given log message to stderr
def log(string):
  if DEBUG: sys.stderr.write("DEBUG: " + string + "\n")

# Generates the GET Request with given headers
def get(domain, has_cookie=False):
    
    if (has_cookie):
        cookie_or_csrf = "csrftoken=" + CSRF + "; sessionid=" + COOKIE
        log(f"Submitting GET request to {domain} using cookie: {cookie_or_csrf}.")
    else:
        log(f"Submitting GET request to {domain}")
        cookie_or_csrf = "csrftoken=" + CSRF

    ''' Implement gzip encoding '''
    request = "GET " + domain + " HTTP/1.1" + CRLF + \
              "Host: " + HOST + CRLF + \
              "Cookie: " + cookie_or_csrf + CRLF + CRLF
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
    #if DEBUG: log(request)
    return request


# Get the csrfmiddlewaretoken from given html
def get_csrfmiddlewaretoken(page):
    csrf_index = page.index("csrfmiddlewaretoken\" value=\"") + 28
    return page[csrf_index:].split("\"")[0]


# Get the csrftoken and sessionId from response
def get_csrftoken_and_cookie(request_response):
    log("Getting CSRF and Session Id")
    cookie_index = response.index("Set-Cookie: sessionid=") + 22
    cook = response[cookie_index:].split(";")[0]

    token_index = response.index("Set-Cookie: csrftoken=") + 22
    token = response[token_index:].split(";")[0]

    return token, cook

# parses a HTTP 1.1 response and converts it to a Dictionary
def parse_response(raw_response):
    log("parse_response: Beginning. Building dictionary...")
    
    resp_list = raw_response.splitlines()
    dictionary = {}
    
    for ii in range(len(resp_list)): 
        curr_line = resp_list[ii]
        
        if ii == 0: # adds status on first line
            log(f"parse_response: {ii}: added [{STATS}] = {curr_line[9:]}")
            dictionary[STATS] = curr_line[9:]
            
        elif curr_line == '': 
            # adds content when first empty line is encountered
            log(f"parse_response: {ii}: encountered empty line, adding rest of response to [{CNTNT}] field")
            rest = "".join(resp_list[ii + 1:-1]) 
            dictionary[CNTNT] = rest
            break
        
        else:
            (header, value) = curr_line.split(":", 1)
            value = value[1:] # trim leading space
            
            if header in RELEVANT_HEADERS:
                
                if header == SETCO:
                    temp = value.split('=')                    
                    header = CSRFT if temp[0] == "csrftoken" else SESID
                    value = temp[1].split(';')[0] 
                        
                dictionary[header] = value
                log(f"parse_response: {ii}: added [{header}] = {value}")
                
    log(f"parse_response: Finished building dictionary  from response")
    return dictionary
            
    
################################################################################


### Setting up the socket ###
log("Creating and wrapping socket...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostbyname(HOST), PORT))  # Connects to the socket

context = ssl.create_default_context()
socket = context.wrap_socket(s, server_hostname=HOST)

### GET Request for login page (to get csrf token) ###
log("Getting initial login page")
socket.send(get(domain='/accounts/login/?next=/fakebook/').encode())
page = socket.recv(3000).decode()
# log("Response: " + page + "\n")

# ### Parsing the login page to find the csrf ###
CSRF = get_csrfmiddlewaretoken(page)
log(f"CSRF from the login page: {CSRF}")

# ### Creating the POST Request ###
log("Posting login information.")
body = f'next=/fakebook/&username={args.username}&password={args.password}&csrfmiddlewaretoken={CSRF}'

# ### Receiving response ###
socket.send(post(domain='/accounts/login/', body=body).encode())
response = socket.recv(3000).decode()

# log("Response: " + response + "\n") 

### Parsing the POST Response to find the cookie ###
log(f"Before logging in: \nCSRF={CSRF} \nCookie={COOKIE}")
response_dict = parse_response(response)
CSRF = response_dict[CSRFT]
COOKIE = response_dict[SESID]
log(f"After logging in: \nCSRF={CSRF} \nCookie={COOKIE}")


### GET Request for homepage ###
''' Make helper to get the current location of the domain from the POST'''
socket.send(get(domain=response_dict[LOCAT], has_cookie=True).encode())
page = socket.recv(3000).decode()

print(page)
