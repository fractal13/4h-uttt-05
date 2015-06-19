#!/bin/bash

while /bin/true; do
    echo "Here we go again."
    UBUNTU_MENUPROXY= python ./uttt_main.py -u lisa -p foobar -a -l 7;
    echo ""
done
