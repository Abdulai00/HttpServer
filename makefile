# Makefile for running the Python HTTP server

.PHONY: run

# Run the Python HTTP server with sudo in the background
run:
	nohup sudo python3 /home/ec2-user/Server/HttpServer/newserver.py > server.log 2>&1 &

