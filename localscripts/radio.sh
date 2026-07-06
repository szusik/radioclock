#!/bin/bash
# amixer -c 1 set Speaker 55%
# mplayer -cache 1024 -nolirc http://stream.rcs.revma.com/ypqt40u0x1zuv

# Play radio 'ns' via local API
curl http://localhost:9980/api/radio/start/ns
