#!/bin/bash
#============================================================
# Description: Create dummy CPU, Memory, Disk, and Network load
# Author: Virwani, Dinesh
#============================================================
# config
remoteIp="username@remoteservername"

# Make sure that your source system's public key is copied into your remote servers root/.ssh
# Command to use
# cat .ssh/id_rsa.pub | ssh username@remoteservername 'cat >> .ssh/authorized_keys'

# Main
# Test will run for 1 hour = 60 min * 60 sec = 3600 seconds
waitTime=3600

# case option will be an argument to the shell script
while [$waitTime -gt 0]
do
	case $1 in
		cpu)
			stress --cpu $2 --io $3 --vm $4 --vm-bytes 128M --timeout 10
			waitTime=$(($waitTime-10))
			;;
		dd)
			dd if=/dev/zero of=file bs=$2 count=1
			waitTime=$(($waitTime-10))
			;;
		scp)
			# Using quite mode to copy file from test server to remote server
			scp -q testfile $remoteIp:~/test

			sleep 5s

			# Using quite mode to copy file from the remote server to test server
			scp -q $remoteIp:~/test/testfile .
			waitTime=$(($waitTime-10))
			;;
		*)
			echo "Unknown command"
			break
			;;
	esac
done