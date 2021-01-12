#!/bin/bash
cd /opt/radioclock/radioclock
waitress-serve-python3 --listen *:80 radioserver:app
