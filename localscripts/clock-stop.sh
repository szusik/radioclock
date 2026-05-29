#!/bin/bash
ps -eaf | grep waitress | grep -v grep | awk '{print $2}' | xargs kill -SIGINT 
