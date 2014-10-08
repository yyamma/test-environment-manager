#!/usr/bin/env python3
import os
import sys
import yaml
import lxc

if __name__ == '__main__':
    if not os.geteuid() == 0:
        print("You need root permission to use this script.")
        sys.exit(1)
