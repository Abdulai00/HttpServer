A simple proxy server hosted on AWS

This project implements a multithreaded HTTP and HTTPS proxy server using Python. The proxy server can handle CONNECT requests to tunnel HTTPS traffic, and also forwards HTTP requests to the target servers. Logging is enabled to track the requests and responses processed by the server.

Features
HTTP/HTTPS Proxy: Supports HTTP and HTTPS traffic.
Multithreaded: Uses threading to handle multiple client requests concurrently.
Tunneling (CONNECT method): Establishes secure tunnels for HTTPS connections.
Logging: Logs requests, responses, and errors for easy debugging and monitoring.
SSL Support: Uses SSL certificates to handle HTTPS connections securely.
