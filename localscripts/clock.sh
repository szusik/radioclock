#!/bin/bash
cd /opt/radioclock/radioclock
waitress-serve --listen *:9980 radioserver:app
