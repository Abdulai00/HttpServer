import http.server
import socketserver
import socket
import threading
import ssl
import select
import requests
import logging

LISTENING_PORT = 8080  
HTTPS_PORT = 443  
CERT_FILE = '/home/ec2-user/Server/HttpServer/bahproxy.com.pem'  
KEY_FILE = '/home/ec2-user/Server/HttpServer/bahproxy.com.key'  
LOG_FILE = 'server.log'  

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def do_CONNECT(self):
        """Handle HTTPS connections via the CONNECT method."""
        logging.info(f"Received CONNECT request for {self.path}")
        host, port = self._parse_connect_path(self.path)
        if host and port == 443:  # Only allow HTTPS connections for tunneling
            logging.debug(f"Parsed CONNECT request - host: {host}, port: {port}")
            target_conn = self._establish_target_connection(host, port)
            if target_conn:
                self._initiate_tunneling(target_conn)
        else:
            self.send_error(400, "Invalid CONNECT request")
            logging.error(f"Invalid CONNECT request: {self.path}")

    def _parse_connect_path(self, path):
        """Parse the CONNECT path to extract host and port."""
        try:
            host, port = path.split(':')
            return host, int(port)
        except ValueError:
            logging.error(f"Error parsing CONNECT path: {path}")
            return None, None

    def _establish_target_connection(self, host, port):
        """Attempt to connect to the target server with a timeout."""
        logging.debug(f"Attempting to connect to {host}:{port}")
        try:
            return socket.create_connection((host, port), timeout=10)  # 10 seconds timeout
        except Exception as e:
            self.send_error(502, "Bad Gateway")
            logging.error(f"Failed to connect to {host}:{port}: {e}")
            return None

    def _initiate_tunneling(self, target_conn):
        """Handle tunneling between client and target connection."""
        logging.info(f"Tunneling connection established for {self.path}")
        self.send_response(200, "Connection Established")
        self.end_headers()
        self.connection.setblocking(0)
        target_conn.setblocking(0)
        self._tunnel_data(self.connection, target_conn)

    def _tunnel_data(self, client_conn, target_conn):
        """Forward data between client and target server."""
        try:
            while True:
                sockets = [client_conn, target_conn]
                read_sockets, _, error_sockets = select.select(sockets, [], sockets, 5)
                if error_sockets or not read_sockets:
                    logging.debug("Error or inactivity detected in tunneling")
                    break  # Close if errors or no activity
                for sock in read_sockets:
                    if sock == client_conn:
                        data = client_conn.recv(8192)
                        if not data:
                            logging.debug("Client disconnected")
                            return  # Client disconnected
                        target_conn.sendall(data)
                    elif sock == target_conn:
                        data = target_conn.recv(8192)
                        if not data:
                            logging.debug("Target server disconnected")
                            return  # Target disconnected
                        client_conn.sendall(data)
        except Exception as e:
            logging.error(f"Error tunneling data: {e}")
        finally:
            client_conn.close()
            target_conn.close()
            logging.info("Closed tunneling connection")

    def do_GET(self):
        logging.info(f"Received GET request for {self.path}")
        self._handle_http_request()

    def do_POST(self):
        logging.info(f"Received POST request for {self.path}")
        self._handle_http_request()

    def do_PUT(self):
        logging.info(f"Received PUT request for {self.path}")
        self._handle_http_request()

    def do_DELETE(self):
        logging.info(f"Received DELETE request for {self.path}")
        self._handle_http_request()

    def _handle_http_request(self):
        """Handle HTTP requests and forward them to the target server."""
        url = self._get_full_url()
        logging.debug(f"Handling HTTP request to {url}")
        if not url:
            self.send_error(400, "Bad Request: Host header missing")
            logging.error(f"Bad Request: Host header missing for {self.path}")
            return

        headers = self._get_request_headers()
        body = self._get_request_body()

        try:
            response = self._forward_request(url, headers, body)
            logging.debug(f"Forwarded request to {url} with response code {response.status_code}")
            self._send_response(response)
        except Exception as e:
            self.send_error(502, "Bad Gateway")
            logging.error(f"Error forwarding request to {url}: {e}")

    def _get_full_url(self):
        """Construct the full URL for the request."""
        host = self.headers.get('Host')
        if host:
            return f"{self.headers.get('X-Forwarded-Proto', 'http')}://{host}{self.path}"
        return None

    def _get_request_headers(self):
        """Retrieve and filter the request headers."""
        headers = dict(self.headers)
        headers.pop('Proxy-Connection', None)  # Remove Proxy-specific headers
        headers.pop('Connection', None)  # 'Connection' should not always be removed; keep-alive might be needed.
        return headers

    def _get_request_body(self):
        """Read the request body."""
        content_length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(content_length) if content_length > 0 else None

    def _forward_request(self, url, headers, body):
        """Forward the request to the target server using the requests library."""
        logging.debug(f"Forwarding request to {url}")
        session = requests.Session()
        req = requests.Request(self.command, url, headers=headers, data=body)
        prepped = session.prepare_request(req)
        settings = session.merge_environment_settings(prepped.url, {}, None, False, None)
        return session.send(prepped, stream=True, verify=False, **settings)

    def _send_response(self, response):
        """Send the response back to the client."""
        logging.debug(f"Sending response with status {response.status_code}")
        self.send_response(response.status_code)
        self._send_response_headers(response)
        self._send_response_body(response)

    def _send_response_headers(self, response):
        """Send filtered headers back to the client."""
        excluded_headers = {
            'Connection', 'Keep-Alive', 'Proxy-Authenticate', 'Proxy-Authorization',
            'TE', 'Trailers', 'Transfer-Encoding', 'Upgrade'
        }
        for header, value in response.headers.items():
            if header not in excluded_headers:
                self.send_header(header, value)
        self.end_headers()

    def _send_response_body(self, response):
        """Send the response body in chunks."""
        logging.debug(f"Sending response body for {self.path}")
        for chunk in response.iter_content(chunk_size=8192):
            self.wfile.write(chunk)
            self.wfile.flush()


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


def start_http_server():
    """Start the HTTP proxy server."""
    logging.info("Starting HTTP server...")
    http_server = ThreadingHTTPServer(('', LISTENING_PORT), ProxyHTTPRequestHandler)
    threading.Thread(target=http_server.serve_forever).start()
    logging.info(f"HTTP proxy server running on port {LISTENING_PORT}")


def start_https_server():
    """Start the HTTPS proxy server."""
    logging.info("Starting HTTPS server...")
    https_server = ThreadingHTTPServer(('', HTTPS_PORT), ProxyHTTPRequestHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    https_server.socket = context.wrap_socket(https_server.socket, server_side=True)
    threading.Thread(target=https_server.serve_forever).start()
    logging.info(f"HTTPS proxy server running on port {HTTPS_PORT}")


def start_proxy_server():
    """Start both HTTP and HTTPS proxy servers."""
    try:
        start_http_server()
        start_https_server()
        while True:
            pass  # Keep the main thread alive
    except KeyboardInterrupt:
        logging.info("Shutting down proxy server.")


if __name__ == "__main__":
    start_proxy_server()
