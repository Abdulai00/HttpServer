import socket
import ssl
import threading
import requests

HEADERSIZE = 10

class HttpObj:
        def __init__(self,method,uri,version) -> None:
            self.type = method
            self.target = uri
            self.version = version
            self.headers_dict = None
            self.body = None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(),1234))

def handle_client(commS, address):
    print(f"New connection to {address}")
    connected = True
    data = ""
    
    while connected:
        chunk = commS.recv(4096).decode('utf-8')
        if not chunk:
            break
        data += chunk

        # Check if we have received the headers completely
        if "\r\n\r\n" in data:
            headers_body_split = data.split("\r\n\r\n", 1)
            request_line, headers = headers_body_split[0].split("\r\n",1)
            
            method , uri, version = request_line.split(" ")
            body = headers_body_split[1] if len(headers_body_split) > 1 else ""
            
            header_dict = parse_headers(headers)
            
            httpobj = HttpObj(method,uri,version)
            httpobj.body = body
            httpobj.headers_dict = header_dict
            
            # If there is a Content-Length header, read the specified amount of body data
            if "Content-Length" in header_dict:
                content_length = int(header_dict["Content-Length"])
                while len(body) < content_length:
                    body += commS.recv(4096).decode('utf-8')
                
            # print(f"Received HTTP request:\nHeaders: {headers}Body: {body}")
            data = ""  # Reset data after processing the complete request
            # Optionally handle the request here
            fulfillRequest(httpobj,commS)
            
        else:
            print("bad")
            
            
    commS.close()
            
def fulfillRequest(httpObj, commS):
    # Make the request using the `requests` library
    try:
        # Handling only GET requests for now
        if httpObj.type == "GET":
            response = requests.get(httpObj.target, headers=httpObj.headers_dict)
        elif httpObj.type == "POST":
            response = requests.post(httpObj.target, headers=httpObj.headers_dict, data=httpObj.body)
        else:
            # Handle unsupported methods
            commS.send("HTTP/1.1 405 Method Not Allowed\r\n\r\n".encode())
            return
        
        # Construct HTTP response to send back to the client
        server_response = f"HTTP/1.1 {response.status_code} {response.reason}\r\n"
        for key, value in response.headers.items():
            server_response += f"{key}: {value}\r\n"
        server_response += "\r\n"  # End headers
        server_response += response.text  # Add response body (HTML, JSON, etc.)
        
        # Send the response back to the client
        print(server_response)
        commS.send(server_response.encode())
    
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

        thread = threading.Thread(target = handle_client, args = (commS,address))
        thread.start()
        
        print(f"active connections:{threading.active_count() -1}")

print("starting server")
start()