#!/bin/bash
amixer -c 1 get Speaker | grep 'Front Left:' | grep -Eo '[0-9]+%' | grep -Eo '[0-9]*'
