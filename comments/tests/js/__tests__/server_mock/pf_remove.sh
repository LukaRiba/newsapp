#!/bin/sh
sudo pfctl -F all -f /etc/pf.conf # Remove port forwarding
sudo pfctl -s nat # Display Current Port Forwarding Rules 