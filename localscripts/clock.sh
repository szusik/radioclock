#!/bin/bash
cd /opt/radioclock/radioclock
waitress-serve-python3 --listen *:9980 radioserver:app
