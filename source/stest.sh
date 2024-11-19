#!/bin/bash

/usr/bin/speedtest-cli --simple | tr  '\n' '  ' &>> /mnt/ramdisk/speedtest.txt
date >> /mnt/ramdisk/speedtest.txt
