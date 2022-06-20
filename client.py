import socket
import random

client = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
client.connect((socket.gethostname() , 8080))

l,h,n = [int(i) for i in client.recv(1024).decode('utf-8').split('\n')]

print("You are worker number : " + str(n))
print(f"received limits : {l} {h}")

while True:
    msg = client.recv(1024).decode("utf-8")
    if msg == '\n':
        r = random.randrange(l,h,1)
        client.send(str(r).encode('utf-8'))
    elif msg == 'end':
        print("You have reached the end!")
        client.close()
        break
    else:
        print(msg)
