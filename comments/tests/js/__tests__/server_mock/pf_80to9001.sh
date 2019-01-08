#!/bin/sh
echo "
rdr pass inet proto tcp from any to any port 80 -> 127.0.0.1 port 9001
" | sudo pfctl -ef -  # Forward Port 80 to 9001 with Mac pfctl Port Forwarding (lines 2, 3 and 4)
sudo pfctl -s nat  # Display Current Port Forwarding Rules 