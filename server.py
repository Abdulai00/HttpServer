import http.server
import socketserver
import socket
import threading
import ssl
import select
import requests

LISTENING_PORT = 8080  
HTTPS_PORT = 443  
CERT_FILE = 'placeholder'  
KEY_FILE = 'placeholder'  


class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def do_GET(self):
        self._handle_http_request()

    def do_POST(self):
        self._handle_http_request()

    def do_PUT(self):
        self._handle_http_request()

    def do_DELETE(self):
        self._handle_http_request()


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def start_http_server():
    """Start the HTTP proxy server."""
    http_server = ThreadingHTTPServer(('', LISTENING_PORT), ProxyHTTPRequestHandler)
    threading.Thread(target=http_server.serve_forever).start()
    print(f"HTTP proxy server running on port {LISTENING_PORT}")


def start_https_server():
    """Start the HTTPS proxy server."""
    https_server = ThreadingHTTPServer(('', HTTPS_PORT), ProxyHTTPRequestHandler)
    https_server.socket = ssl.wrap_socket(
        https_server.socket,
        server_side=True,
        certfile=CERT_FILE,
        keyfile=KEY_FILE,
        ssl_version=ssl.PROTOCOL_TLS
    )
    threading.Thread(target=https_server.serve_forever).start()
    print(f"HTTPS proxy server running on port {HTTPS_PORT}")


def start_proxy_server():
    """Start both HTTP and HTTPS proxy servers."""
    start_http_server()
    start_https_server()


if __name__ == "__main__":
    start_proxy_server()
