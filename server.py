import socket
import ssl
import threading
import requests

HEADERSIZE = 64

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(),1234))


def handle_client(commS,address):
    print(f"New connection to {address}")
    connected = True
    while connected:
        msg_length = commS.recv(HEADERSIZE).decode('utf-8')
        if msg_length:
            msg_length = int(msg_length)
            msg = commS.recv(msg_length).decode('utf-8')
            if len(msg) == 0:
                connected = False

            print("the message from {address} is {msg}")

    commS.close()
    
class HttpObj:
        def __init__(self,method,uri,version) -> None:
            self.type = method
            self.target = uri
            self.version = version
            self.headers_dict = None
            self.body = None
            
def parse_http(msg):
    
     
    if "\r\n" in msg:
        
        request_line, headers_body = msg.split("\r\n", 1)
        headers = headers_body.splitlines()
        body = ""
        header_dict = {}
        
        for i in range(len(headers)):
            
            if(len(headers[i]) == 0):
                body = headers[i+1]
                break
            
        for header in headers:
            if(len(header) == 0):
                break
            
            key, value = header.split(": ",1)
            
            header_dict[key] = value
            
    else:
        raise ValueError("Invalid HTTP request: Missing CRLF delimiter")
    
    method , uri , version = request_line.split(" ")
    
    httpObj = HttpObj(method,uri,version)
    httpObj.headers_dict = header_dict
    httpObj.body = body
    
    print(header_dict)
    print(body)
    
    return httpObj
    
    
def start():
    s.listen(5)
    while True:
        commS , address = s.accept

        thread = threading.Thread(target = handle_client, args = (commS,address))
        thread.start
        print(f"active connections:{threading.activeCount() -1}")


#print("starting server")
testString = "POST /cgi-bin/process.cgi HTTP/1.1\r\nUser-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)\r\nHost: www.tutorialspoint.com\r\n\
Content-Type: application/x-www-form-urlencoded\r\nContent-Length: length\r\nAccept-Language: en-us\r\nAccept-Encoding: gzip, deflate\r\nConnection: Keep-Alive\
\r\n\r\nBlah blah"
obj = parse_http(testString)

#print(obj.type)
#print(obj.target)
#print(obj.version)