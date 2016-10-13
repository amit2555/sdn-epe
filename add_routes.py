#!/usr/bin/env python

import time
from sys import stdout


messages = ['announce route 10.2.3.3/32 next-hop 2.2.2.2 label 17 local-preference 65000']

for message in messages:
    stdout.write(message + '\n')
    stdout.flush()
    time.sleep(1)

while True:
    time.sleep(1)
