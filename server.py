import socket
import ssl
import threading 


HEADERSIZE = 64

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(),1234))


def handle_client(commS,address):
    print(f"New connection to {address}")
    connected = True
    while connected:
        msg_length = commS.recv(HEADERSIZE).decode('utf-8')
        msg_length = int(msg_length)
        msg = commS.recv(msg_length).decode('utf-8')
        if len(msg) == 0:
            connected = False

        print("the message from {address} is {msg}")

    commS.close()
    
class HttpObj:
        def __init__(self,method,uri,version) -> None:
            self.type = type
            self.target = uri
            self.version = version
    
def parse_http(msg):
    
    http = {
        "GET" : "",
        "DELETE" : "",
        "PUT" : "",
        "POST" : "",
        
    }
     
     
    request_line, headers_body = msg.spilt("\r\n")
    
    method , uri , version = request_line.split(" ")
    
    if method not in http:
        return None
    
    
    
    
    httpObj = HttpObj(method,uri,version)
    
    return httpObj
    
    
    

def start():
    s.listen(5)
    while True:
        commS , address = s.accept

        thread = threading.Thread(target = handle_client, args = (commS,address))
        thread.start
        print(f"active connections:{threading.activeCount() -1}")


print("starting server")
start()