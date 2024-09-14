import socket
import ssl
import threading
import requests

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0",443))

PrivateKey = "/home/ec2-user/Server/HttpServer/bahproxy.com.key"
Certification = "/home/ec2-user/Server/HttpServer/bahproxy.com.pem"

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=Certification,keyfile=PrivateKey)
  
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
