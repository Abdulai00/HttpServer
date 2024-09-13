import socket
import ssl
import threading
import requests

class HttpObj:
        def __init__(self,method,uri,version) -> None:
            self.type = method
            self.target = uri
            self.version = version
            self.headers_dict = None
            self.body = None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0",443))

PrivateKey = "/home/ec2-user/Server/HttpServer/bahproxy.com.key"
Certification = "/home/ec2-user/Server/HttpServer/bahproxy.com.pem"


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=Certification,keyfile=PrivateKey)

def handle_client(commS, address):
    print(f"New connection to {address}")
    commS.settimeout(10)  
    connected = True
    data = ""

    try:
        while connected:
            try:
                # Receive data from the client
                chunk = commS.recv(4096)
                
                # Handle client disconnect
                if not chunk:
                    print(f"Client at {address} disconnected.")
                    break
                
                data += chunk.decode('utf-8')

                if "\r\n\r\n" in data:
                    headers_body_split = data.split("\r\n\r\n", 1)
                    
                    # Split request line and headers
                    try:
                        request_line, headers = headers_body_split[0].split("\r\n", 1)
                        method, uri, version = request_line.split(" ")

                        # Basic validation of the HTTP version
                        if not version.startswith("HTTP/"):
                            raise ValueError("Invalid HTTP version")
                    
                    except ValueError:
                        # If request is malformed, send 400 Bad Request
                        commS.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode())
                        break  # Exit after sending the bad request response

                    body = headers_body_split[1] if len(headers_body_split) > 1 else ""
                    header_dict = parse_headers(headers)

                    httpobj = HttpObj(method, uri, version)
                    httpobj.body = body
                    httpobj.headers_dict = header_dict

                    if "Content-Length" in header_dict:
                        content_length = int(header_dict["Content-Length"])
                        while len(body) < content_length:
                            body += commS.recv(4096).decode('utf-8')
                    
                    data = ""  # Reset data after processing
                    fulfillRequest(httpobj, commS)

            except socket.timeout:
                print(f"Connection at {address} timed out waiting for data.")
                break
            
            except ConnectionResetError:
                print(f"Connection reset by client {address}.")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        commS.close()
        print("Connection closed.")
            
def fulfillRequest(httpObj, commS):
    # Make the request using the `requests` library
    try:
        # Handling only GET requests for now
        if httpObj.type == "GET":
            response = requests.get(httpObj.target, headers=httpObj.headers_dict)
            
        elif httpObj.type == "POST":
            response = requests.post(httpObj.target, headers=httpObj.headers_dict, data=httpObj.body)
            
        elif httpObj.type == "DELETE":
            response = requests.delete(httpObj.target, headers=httpObj.headers_dict)
            
        elif httpObj.type == "PUT":
            response = requests.put(httpObj.target, headers=httpObj.headers_dict, data=httpObj.body)
            
        else:
            # Handle unsupported methods
            commS.send("HTTP/1.1 405 Method Not Allowed\r\n\r\n".encode())
            return
        
        server_response = f"HTTP/1.1 {response.status_code} {response.reason}\r\n"
        for key, value in response.headers.items():
            server_response += f"{key}: {value}\r\n"
        server_response += "\r\n"  # End headers
        
        # Send headers and body separately to handle larger responses
        commS.send(server_response.encode())

        # Send the body in chunks if it's large to prevent memory overload
        for chunk in response.iter_content(chunk_size=4096):
            commS.send(chunk)
        
        # Send the response back to the client
        print(server_response)
        #commS.send(server_response.encode())
    
    except requests.exceptions.RequestException as e:
        # If there was an error making the request, send an error response
        error_response = f"HTTP/1.1 500 Internal Server Error\r\n\r\nError: {str(e)}"
        commS.send(error_response.encode())
            
def parse_headers(header_list):
    header_dict = {}
    header_list = header_list.split("\r\n")
    
    for header in header_list:
        key, value = header.split(": ",1)   
        header_dict[key] = value
      
    return header_dict
  
def start():
    s.listen(5)
    while True:
        commS , address = s.accept()
        tls_comms = context.wrap_socket(commS,server_side=True)
        thread = threading.Thread(target = handle_client, args = (tls_comms,address))
        thread.start()
        
        print(f"active connections:{threading.active_count() -1}")

print("Listening for incoming traffic")
start()
