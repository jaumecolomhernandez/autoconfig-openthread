import sys, socket 

if len(sys.argv)>1:
        mes = sys.argv[1]
else:
        mes = "example"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', 12344))
        sock.sendall(bytes(mes, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))