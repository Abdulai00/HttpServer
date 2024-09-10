import socket

# Create a connection to the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

# The HTTP request string to send to the proxy server
testString = (
    "GET http://example.com/ HTTP/1.1\r\n"
    "Host: example.com\r\n"
    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36\r\n"
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n"
    "Accept-Language: en-US,en;q=0.5\r\n"
    "Connection: close\r\n"  # Close after the response is complete
    "\r\n"
)

# Send the request to the proxy server
s.send(testString.encode())
print("Sent the message")

# Receive the response from the server
response = b""  # Collect the response as bytes
while True:
    chunk = s.recv(4096)  # Receive as bytes
    if not chunk:
        break
    response += chunk  # Append the bytes

# Close the connection after receiving the response
s.close()

# Now decode the response to handle headers and body separately
response_str = response.decode('utf-8', errors='replace')  # Replace problematic characters if needed
headers, body = response_str.split("\r\n\r\n", 1)

print("Headers:")
print(headers)
print("\nBody:")
print(body)

print("Disconnected")
