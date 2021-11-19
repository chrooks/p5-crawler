#!/usr/bin/env python3

import argparse, socket, ssl

### Debug ###
# DEBUG = True
DEBUG = False

### Argument Parser ####
parser = argparse.ArgumentParser(description='crawl the web')
parser.add_argument('username', type=str, help="Username")
parser.add_argument('networks', type=str, help="Password")
args = parser.parse_args()