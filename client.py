import socket

HEADERSIZE = 10  # Assuming 10 bytes are used for the message length header

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

testString = (
    "GET http://example.com/ HTTP/1.1\r\n"
    "Host: example.com\r\n"
    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36\r\n"
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n"
    "Accept-Language: en-US,en;q=0.5\r\n"
    "Connection: keep-alive\r\n\r\n"
)

s.send(testString.encode())

print("Sent the message")
while True:
    full_msg = ""
    new_msg = True

    while True:
        msg = s.recv(16)
        if new_msg:
            print(f"New message length: {msg[:HEADERSIZE]}")
            msglen = int(msg[:HEADERSIZE])
            print(msglen)
            new_msg = False

        full_msg += msg.decode()

        if len(full_msg) - HEADERSIZE == msglen:
            print("Received full message")
            print(full_msg[HEADERSIZE:])
            break  # Exit after receiving the full message
    break

s.close()
print("Disconnected")